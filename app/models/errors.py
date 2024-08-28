from pydantic import BaseModel
from typing import List

class ErrorResponse(BaseModel):
    status: str
    message: str
    status_code: int

class ValidationErrorDetail(BaseModel):
    field: str
    message: str

class ValidationErrorResponse(BaseModel):
    errors: List[ValidationErrorDetail]