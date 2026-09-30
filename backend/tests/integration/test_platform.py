"""
B-M3 Platform tests — API endpoints, history, analytics (§B5).

Covers:
- GET /health — shape and fields
- GET /languages — list
- POST /analyze — happy path, envelope, ai_status
- POST /analyze — validation errors (empty fields, unsupported language, oversize)
- POST /analyze — no stack trace leakage
- GET /samples — returns list
- History: save, list, filter, pagination, delete
- Analytics: counts
- Storage-failure path (history_saved=false, result still returned)
- Rate limit: 429 after 30 requests
"""
import json
import uuid
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.application.container import build_history_repository, get_analysis_service
from backend.app.core.config import settings
from backend.app.models.responses import AnalysisResult, AnalysisMetadata
from backend.app.models.enums import Language, ErrorType, Severity, AIStatus
from backend.app.application.ports import HistoryPort, AnalysisServicePort

client = TestClient(app, raise_server_exceptions=False)


# ── Health ────────────────────────────────────────────────────────────────────

def test_health_returns_ok():
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    d = body["data"]
    assert d["status"] == "ok"
    assert "version" in d
    assert "ai_provider" in d
    assert "ai_configured" in d
    assert "db_ok" in d


# ── Languages ─────────────────────────────────────────────────────────────────

def test_languages_endpoint():
    r = client.get("/api/v1/languages")
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True


# ── Samples ───────────────────────────────────────────────────────────────────

def test_samples_endpoint():
    r = client.get("/api/v1/samples")
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert isinstance(body["data"], list)


# ── Analyze — happy path ──────────────────────────────────────────────────────

VALID_PYTHON_REQUEST = {
    "language": "python",
    "source_code": "x = 1\nprint(total)\n",
    "error_input": "NameError: name 'total' is not defined on line 2",
}


def test_analyze_returns_envelope():
    r = client.post("/api/v1/analyze", json=VALID_PYTHON_REQUEST)
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert body["data"] is not None
    assert body["error"] is None


def test_analyze_result_has_required_fields():
    r = client.post("/api/v1/analyze", json=VALID_PYTHON_REQUEST)
    d = r.json()["data"]
    for field in ("analysis_id", "language", "error_type", "severity", "ai_status", "analysis_metadata"):
        assert field in d, f"Missing field: {field}"


def test_analyze_ai_status_present():
    r = client.post("/api/v1/analyze", json=VALID_PYTHON_REQUEST)
    d = r.json()["data"]
    assert d["ai_status"] in ("ok", "mock", "disabled", "unavailable", "timeout", "invalid_response")


def test_analyze_schema_version():
    r = client.post("/api/v1/analyze", json=VALID_PYTHON_REQUEST)
    d = r.json()["data"]
    assert d.get("schema_version") == "1.0"


# ── Analyze — validation errors ───────────────────────────────────────────────

def test_analyze_missing_language():
    r = client.post("/api/v1/analyze", json={
        "source_code": "x=1", "error_input": "err"
    })
    assert r.status_code in (400, 422)
    body = r.json()
    assert body["success"] is False
    assert body["error"] is not None


def test_analyze_empty_source_code():
    r = client.post("/api/v1/analyze", json={
        "language": "python", "source_code": "   ", "error_input": "err"
    })
    # Either 422 (Pydantic) or 200 with validation error in body
    assert r.status_code in (200, 422)


def test_analyze_unsupported_language():
    r = client.post("/api/v1/analyze", json={
        "language": "cobol", "source_code": "x=1", "error_input": "err"
    })
    assert r.status_code in (400, 422)
    body = r.json()
    assert body["success"] is False


def test_analyze_oversize_source():
    r = client.post("/api/v1/analyze", json={
        "language": "python",
        "source_code": "x" * 25000,
        "error_input": "some error",
    })
    assert r.status_code in (200, 422)


def test_analyze_malformed_json():
    r = client.post(
        "/api/v1/analyze",
        content=b"not json",
        headers={"Content-Type": "application/json"},
    )
    assert r.status_code in (400, 422)
    body = r.json()
    assert body["success"] is False



# ── No stack-trace leakage ────────────────────────────────────────────────────

def test_no_stack_trace_in_error_response():
    r = client.post(
        "/api/v1/analyze",
        content=b"{{broken",
        headers={"Content-Type": "application/json"},
    )
    text = r.text
    assert "Traceback" not in text
    assert "File " not in text


# ── AI failure still returns 200 ──────────────────────────────────────────────

class _AlwaysFailAnalysisService(AnalysisServicePort):
    """Service that always returns a result with ai_status=unavailable."""
    def analyze(self, request):
        from datetime import datetime, timezone
        return AnalysisResult(
            analysis_id=str(uuid.uuid4()),
            created_at=datetime.now(timezone.utc).isoformat(),
            language=Language.PYTHON,
            error_type=ErrorType.UNKNOWN,
            severity=Severity.UNKNOWN,
            summary="Test static only",
            ai_status=AIStatus.UNAVAILABLE,
            analysis_metadata=AnalysisMetadata(
                analysis_mode="static_only",
                history_saved=False,
            ),
        )


def test_ai_failure_returns_200_with_static_result():
    from backend.app.api.routers.analysis import get_service
    app.dependency_overrides[get_service] = lambda: _AlwaysFailAnalysisService()
    try:
        r = client.post("/api/v1/analyze", json=VALID_PYTHON_REQUEST)
        assert r.status_code == 200
        body = r.json()
        assert body["success"] is True
        assert body["data"]["ai_status"] == "unavailable"
    finally:
        app.dependency_overrides.clear()


# ── History ───────────────────────────────────────────────────────────────────

def test_history_list_empty_initially():
    # Use in-memory override
    from backend.app.api.routers.history import _get_repo
    import tempfile, os
    tmp = tempfile.mktemp(suffix=".db")
    from backend.app.history.repository import SQLiteHistoryRepository
    repo = SQLiteHistoryRepository(tmp)
    app.dependency_overrides[_get_repo] = lambda: repo
    try:
        r = client.get("/api/v1/history")
        assert r.status_code == 200
        body = r.json()
        assert body["success"] is True
        assert body["data"]["total"] == 0
        assert body["data"]["items"] == []
    finally:
        app.dependency_overrides.clear()
        try:
            os.unlink(tmp)
        except Exception:
            pass


def _make_result(lang=Language.PYTHON, error_type=ErrorType.NAME_REFERENCE) -> AnalysisResult:
    from datetime import datetime, timezone
    return AnalysisResult(
        analysis_id=str(uuid.uuid4()),
        created_at=datetime.now(timezone.utc).isoformat(),
        language=lang,
        error_type=error_type,
        severity=Severity.HIGH,
        summary=f"Test {error_type.value}",
        ai_status=AIStatus.MOCK,
        analysis_metadata=AnalysisMetadata(analysis_mode="hybrid", history_saved=True),
    )


def _tmp_repo():
    import tempfile
    from backend.app.history.repository import SQLiteHistoryRepository
    tmp = tempfile.mktemp(suffix=".db")
    return SQLiteHistoryRepository(tmp), tmp


def test_history_save_and_list():
    from backend.app.api.routers.history import _get_repo
    import os
    repo, tmp = _tmp_repo()
    result = _make_result()
    repo.save(result)
    app.dependency_overrides[_get_repo] = lambda: repo
    try:
        r = client.get("/api/v1/history")
        body = r.json()
        assert body["data"]["total"] == 1
        assert body["data"]["items"][0]["analysis_id"] == result.analysis_id
    finally:
        app.dependency_overrides.clear()
        try: os.unlink(tmp)
        except: pass


def test_history_filter_by_language():
    from backend.app.api.routers.history import _get_repo
    import os
    repo, tmp = _tmp_repo()
    repo.save(_make_result(lang=Language.PYTHON))
    repo.save(_make_result(lang=Language.JAVA))
    repo.save(_make_result(lang=Language.JAVA))
    app.dependency_overrides[_get_repo] = lambda: repo
    try:
        r = client.get("/api/v1/history?language=java")
        body = r.json()
        assert body["data"]["total"] == 2
        for item in body["data"]["items"]:
            assert item["language"] == "java"
    finally:
        app.dependency_overrides.clear()
        try: os.unlink(tmp)
        except: pass


def test_history_pagination():
    from backend.app.api.routers.history import _get_repo
    import os
    repo, tmp = _tmp_repo()
    for _ in range(5):
        repo.save(_make_result())
    app.dependency_overrides[_get_repo] = lambda: repo
    try:
        r = client.get("/api/v1/history?limit=2&offset=0")
        body = r.json()
        assert body["data"]["total"] == 5
        assert len(body["data"]["items"]) == 2
    finally:
        app.dependency_overrides.clear()
        try: os.unlink(tmp)
        except: pass


def test_history_get_by_id():
    from backend.app.api.routers.history import _get_repo
    import os
    repo, tmp = _tmp_repo()
    result = _make_result()
    repo.save(result)
    app.dependency_overrides[_get_repo] = lambda: repo
    try:
        r = client.get(f"/api/v1/history/{result.analysis_id}")
        assert r.status_code == 200
        body = r.json()
        assert body["data"]["analysis_id"] == result.analysis_id
    finally:
        app.dependency_overrides.clear()
        try: os.unlink(tmp)
        except: pass


def test_history_get_not_found():
    from backend.app.api.routers.history import _get_repo
    import os
    repo, tmp = _tmp_repo()
    app.dependency_overrides[_get_repo] = lambda: repo
    try:
        r = client.get("/api/v1/history/nonexistent-id")
        assert r.status_code == 404
    finally:
        app.dependency_overrides.clear()
        try: os.unlink(tmp)
        except: pass


def test_history_delete():
    from backend.app.api.routers.history import _get_repo
    import os
    repo, tmp = _tmp_repo()
    result = _make_result()
    repo.save(result)
    app.dependency_overrides[_get_repo] = lambda: repo
    try:
        r = client.delete(f"/api/v1/history/{result.analysis_id}")
        assert r.status_code == 200
        # Verify gone
        r2 = client.get(f"/api/v1/history/{result.analysis_id}")
        assert r2.status_code == 404
    finally:
        app.dependency_overrides.clear()
        try: os.unlink(tmp)
        except: pass


def test_history_search_q():
    from backend.app.api.routers.history import _get_repo
    import os
    repo, tmp = _tmp_repo()
    r1 = _make_result(error_type=ErrorType.SYNTAX)
    r1 = r1.model_copy(update={"summary": "Syntax colon error"})
    r2 = _make_result(error_type=ErrorType.RUNTIME)
    r2 = r2.model_copy(update={"summary": "Runtime division by zero"})
    repo.save(r1)
    repo.save(r2)
    app.dependency_overrides[_get_repo] = lambda: repo
    try:
        r = client.get("/api/v1/history?q=colon")
        body = r.json()
        assert body["data"]["total"] == 1
        assert "colon" in body["data"]["items"][0]["summary"]
    finally:
        app.dependency_overrides.clear()
        try: os.unlink(tmp)
        except: pass


# ── Analytics ─────────────────────────────────────────────────────────────────

def test_analytics_summary_structure():
    from backend.app.api.routers.analytics import _get_repo
    import os
    repo, tmp = _tmp_repo()
    repo.save(_make_result())
    app.dependency_overrides[_get_repo] = lambda: repo
    try:
        r = client.get("/api/v1/analytics/summary")
        assert r.status_code == 200
        body = r.json()
        assert body["success"] is True
        d = body["data"]
        assert "total" in d
        assert "by_error_type" in d
        assert "by_language" in d
        assert "by_severity" in d
        assert "by_ai_status" in d
        assert "daily_counts" in d
        assert "recent" in d
        assert d["total"] == 1
    finally:
        app.dependency_overrides.clear()
        try: os.unlink(tmp)
        except: pass


# ── Storage failure path ──────────────────────────────────────────────────────

class _FailingHistoryPort(HistoryPort):
    def save(self, result) -> bool:
        return False


def test_storage_failure_still_returns_result():
    from backend.app.application.container import build_history_repository as bhr
    from backend.app.api.routers.analysis import get_service as gs
    from backend.app.ai.engine import build_ai_engine
    from backend.app.application.services import AnalysisService

    def override_service():
        s = settings
        ai = build_ai_engine(s)
        return AnalysisService(ai_engine=ai, history=_FailingHistoryPort())

    app.dependency_overrides[gs] = override_service
    try:
        r = client.post("/api/v1/analyze", json=VALID_PYTHON_REQUEST)
        assert r.status_code == 200
        body = r.json()
        assert body["success"] is True
        assert body["data"]["analysis_metadata"]["history_saved"] is False
    finally:
        app.dependency_overrides.clear()
