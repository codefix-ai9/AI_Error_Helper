from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import List, Optional
import uuid
from backend.app.models.envelope import Envelope, ErrorResponse, ErrorDetail

class BaseAppException(Exception):
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", status_code: int = 500, details: Optional[List[ErrorDetail]] = None):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or []
        super().__init__(self.message)

class ValidationException(BaseAppException):
    def __init__(self, message: str, details: Optional[List[ErrorDetail]] = None):
        super().__init__(message=message, code="VALIDATION_ERROR", status_code=400, details=details)

def register_error_handlers(app: FastAPI):
    @app.exception_handler(BaseAppException)
    async def app_exception_handler(request: Request, exc: BaseAppException):
        req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        error_resp = ErrorResponse(code=exc.code, message=exc.message, details=exc.details, request_id=req_id)
        envelope = Envelope(success=False, data=None, error=error_resp)
        return JSONResponse(status_code=exc.status_code, content=envelope.model_dump())

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        details = [ErrorDetail(field=".".join(map(str, e["loc"])), message=e["msg"]) for e in exc.errors()]
        error_resp = ErrorResponse(code="VALIDATION_ERROR", message="The request could not be understood.", details=details, request_id=req_id)
        envelope = Envelope(success=False, data=None, error=error_resp)
        return JSONResponse(status_code=400, content=envelope.model_dump())

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        # Log the error here in a real app
        error_resp = ErrorResponse(code="INTERNAL_ERROR", message="An unexpected error occurred.", details=[], request_id=req_id)
        envelope = Envelope(success=False, data=None, error=error_resp)
        return JSONResponse(status_code=500, content=envelope.model_dump())
