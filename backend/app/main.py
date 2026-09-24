from fastapi import FastAPI
from backend.app.core.config import settings
from backend.app.core.errors import register_error_handlers
from backend.app.core.logging import setup_logging

setup_logging()

app = FastAPI(title="AI Error Helper")
register_error_handlers(app)

@app.get("/health")
def health_check():
    return {"status": "ok"}
