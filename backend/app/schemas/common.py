from pydantic import BaseModel
from typing import Any, Optional

class SuccessResponse(BaseModel):
    status: str = "success"
    data: Any
    message: Optional[str] = None

class ErrorResponse(BaseModel):
    status: str = "error"
    error: str
