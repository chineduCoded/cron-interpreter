from fastapi import HTTPException
from app.models.errors import ErrorResponse

class CustomHTTPException(HTTPException):
    def __init__(self, status_code: int, detail: str, status_msg: str, headers: dict = None):
        error_response = ErrorResponse(
            status=status_msg,
            message=detail,
            status_code=status_code
        ).model_dump()
        super().__init__(status_code=status_code, detail=error_response, headers=headers)