"""
FastAPI application entry point (§B-M3).
"""
import time
import uuid
import logging
from collections import defaultdict, deque
from threading import Lock

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.core.config import settings
from backend.app.core.errors import register_error_handlers
from backend.app.core.logging import setup_logging
from backend.app.api.routers import analysis, health, languages, history, analytics, samples

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Error Helper", version="1.0.0")

# ── CORS ───────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list + [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Rate Limiter (in-memory, per IP, 30/min on /analyze) ──────────────────
_rl_lock = Lock()
_rl_windows: dict = defaultdict(lambda: deque())
_RL_LIMIT = 30       # requests
_RL_WINDOW = 60.0    # seconds


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    request.state.request_id = request_id

    if request.url.path == "/api/v1/analyze" and request.method == "POST":
        client_ip = request.client.host if request.client else "unknown"
        now = time.monotonic()
        with _rl_lock:
            window = _rl_windows[client_ip]
            # Evict old entries
            while window and window[0] < now - _RL_WINDOW:
                window.popleft()
            if len(window) >= _RL_LIMIT:
                logger.warning("Rate limit hit for IP %s request_id=%s", client_ip, request_id)
                return JSONResponse(
                    status_code=429,
                    content={
                        "success": False,
                        "data": None,
                        "error": {
                            "code": "RATE_LIMIT_EXCEEDED",
                            "message": "Too many requests. Please wait before submitting again.",
                            "details": [],
                            "request_id": request_id,
                        },
                    },
                )
            window.append(now)

    response: Response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# ── Error handlers ─────────────────────────────────────────────────────────
register_error_handlers(app)

# ── Routers ────────────────────────────────────────────────────────────────
app.include_router(health.router,     prefix="/api/v1")
app.include_router(analysis.router,   prefix="/api/v1")
app.include_router(languages.router,  prefix="/api/v1")
app.include_router(history.router,    prefix="/api/v1")
app.include_router(analytics.router,  prefix="/api/v1")
app.include_router(samples.router,    prefix="/api/v1")
