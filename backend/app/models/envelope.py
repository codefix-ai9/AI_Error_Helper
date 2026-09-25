from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, Any

T = TypeVar("T")

class ErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str

class ErrorResponse(BaseModel):
    code: str
    message: str
    details: list[ErrorDetail] = []
    request_id: Optional[str] = None

class Envelope(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[ErrorResponse] = None
