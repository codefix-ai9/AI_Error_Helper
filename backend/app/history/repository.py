"""
SQLite HistoryRepository (§9).

Parameterized queries only. Storage failure is non-fatal.
Table: analyses
  id TEXT PK, created_at TEXT, language TEXT, error_type TEXT,
  severity TEXT, line INTEGER, summary TEXT, ai_status TEXT, result_json TEXT
Indexes: created_at, language, error_type.
"""
import json
import logging
import sqlite3
import threading
from pathlib import Path
from typing import List, Optional, Tuple

from backend.app.application.ports import HistoryPort
from backend.app.models.responses import AnalysisResult, HistoryItem, AnalyticsSummary
from backend.app.core.config import Settings

logger = logging.getLogger(__name__)

_DDL = """
CREATE TABLE IF NOT EXISTS analyses (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    language TEXT NOT NULL,
    error_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    line INTEGER,
    summary TEXT NOT NULL,
    ai_status TEXT NOT NULL,
    result_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_created_at  ON analyses (created_at);
CREATE INDEX IF NOT EXISTS idx_language    ON analyses (language);
CREATE INDEX IF NOT EXISTS idx_error_type  ON analyses (error_type);
"""


def _db_path_from_settings(settings: Settings) -> str:
    raw = settings.DB_PATH
    # Strip "sqlite:///" prefix if present
    if raw.startswith("sqlite:///"):
        raw = raw[len("sqlite:///"):]
    return raw


class SQLiteHistoryRepository(HistoryPort):
    """Thread-safe SQLite repository."""

    def __init__(self, db_path: str):
        self._db_path = db_path
        self._lock = threading.Lock()
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def _init_db(self) -> None:
        Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
        with self._lock:
            with self._connect() as conn:
                conn.executescript(_DDL)

    # ── HistoryPort ────────────────────────────────────────────────────────

    def save(self, result: AnalysisResult) -> bool:
        try:
            line = result.location.line if result.location else None
            result_json = result.model_dump_json()
            with self._lock:
                with self._connect() as conn:
                    conn.execute(
                        """INSERT OR REPLACE INTO analyses
                           (id, created_at, language, error_type, severity,
                            line, summary, ai_status, result_json)
                           VALUES (?,?,?,?,?,?,?,?,?)""",
                        (
                            result.analysis_id,
                            result.created_at,
                            result.language.value if hasattr(result.language, "value") else str(result.language),
                            result.error_type.value if hasattr(result.error_type, "value") else str(result.error_type),
                            result.severity.value if hasattr(result.severity, "value") else str(result.severity),
                            line,
                            result.summary,
                            result.ai_status.value if hasattr(result.ai_status, "value") else str(result.ai_status),
                            result_json,
                        ),
                    )
            return True
        except Exception as e:
            logger.error("History save failed: %s", e)
            return False

    # ── Query helpers ──────────────────────────────────────────────────────

    def list_items(
        self,
        q: Optional[str] = None,
        language: Optional[str] = None,
        error_type: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Tuple[List[HistoryItem], int]:
        """Return (items, total_count) matching filters."""
        conditions = []
        params: list = []

        if q:
            conditions.append("(summary LIKE ? OR error_type LIKE ? OR language LIKE ?)")
            like = f"%{q}%"
            params.extend([like, like, like])
        if language:
            conditions.append("language = ?")
            params.append(language)
        if error_type:
            conditions.append("error_type = ?")
            params.append(error_type)
        if severity:
            conditions.append("severity = ?")
            params.append(severity)

        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

        with self._lock:
            with self._connect() as conn:
                count_row = conn.execute(
                    f"SELECT COUNT(*) FROM analyses {where}", params
                ).fetchone()
                total = count_row[0] if count_row else 0

                rows = conn.execute(
                    f"""SELECT id, created_at, language, error_type, severity, summary
                        FROM analyses {where}
                        ORDER BY created_at DESC
                        LIMIT ? OFFSET ?""",
                    params + [limit, offset],
                ).fetchall()

        items = [
            HistoryItem(
                analysis_id=r["id"],
                created_at=r["created_at"],
                language=r["language"],
                error_type=r["error_type"],
                severity=r["severity"],
                summary=r["summary"],
            )
            for r in rows
        ]
        return items, total

    def get_by_id(self, analysis_id: str) -> Optional[AnalysisResult]:
        with self._lock:
            with self._connect() as conn:
                row = conn.execute(
                    "SELECT result_json FROM analyses WHERE id = ?", (analysis_id,)
                ).fetchone()
        if not row:
            return None
        return AnalysisResult.model_validate_json(row["result_json"])

    def delete_by_id(self, analysis_id: str) -> bool:
        with self._lock:
            with self._connect() as conn:
                cursor = conn.execute(
                    "DELETE FROM analyses WHERE id = ?", (analysis_id,)
                )
        return cursor.rowcount > 0

    def analytics_summary(self) -> dict:
        """Return aggregate counts for analytics endpoint (§9)."""
        with self._lock:
            with self._connect() as conn:
                total = conn.execute("SELECT COUNT(*) FROM analyses").fetchone()[0]

                by_error_type = {
                    r[0]: r[1]
                    for r in conn.execute(
                        "SELECT error_type, COUNT(*) FROM analyses GROUP BY error_type"
                    ).fetchall()
                }
                by_language = {
                    r[0]: r[1]
                    for r in conn.execute(
                        "SELECT language, COUNT(*) FROM analyses GROUP BY language"
                    ).fetchall()
                }
                by_severity = {
                    r[0]: r[1]
                    for r in conn.execute(
                        "SELECT severity, COUNT(*) FROM analyses GROUP BY severity"
                    ).fetchall()
                }
                by_ai_status = {
                    r[0]: r[1]
                    for r in conn.execute(
                        "SELECT ai_status, COUNT(*) FROM analyses GROUP BY ai_status"
                    ).fetchall()
                }
                # Daily counts last 30 days (UTC date)
                daily_counts = {
                    r[0]: r[1]
                    for r in conn.execute(
                        """SELECT strftime('%Y-%m-%d', created_at) as day, COUNT(*)
                           FROM analyses
                           WHERE created_at >= datetime('now', '-30 days')
                           GROUP BY day
                           ORDER BY day"""
                    ).fetchall()
                }
                # Recent last 10
                recent_rows = conn.execute(
                    """SELECT id, created_at, language, error_type, severity, summary
                       FROM analyses ORDER BY created_at DESC LIMIT 10"""
                ).fetchall()
                recent = [
                    {
                        "analysis_id": r["id"],
                        "created_at": r["created_at"],
                        "language": r["language"],
                        "error_type": r["error_type"],
                        "severity": r["severity"],
                        "summary": r["summary"],
                    }
                    for r in recent_rows
                ]

        return {
            "total": total,
            "by_error_type": by_error_type,
            "by_language": by_language,
            "by_severity": by_severity,
            "by_ai_status": by_ai_status,
            "daily_counts": daily_counts,
            "recent": recent,
        }


def build_history_repository(settings: Settings) -> HistoryPort:
    db_path = _db_path_from_settings(settings)
    return SQLiteHistoryRepository(db_path)
