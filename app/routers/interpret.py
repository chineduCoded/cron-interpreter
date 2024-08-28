from fastapi import APIRouter, status

from app.models.cron import CronExpression
from app.services.interpret_service import interpret_cron_expression
from app.utils.custom_exception import CustomHTTPException

router = APIRouter()

@router.post("/", summary="Interpret Cron expression", status_code=status.HTTP_200_OK)
def interpret_cron(cron: CronExpression):
    try:
        result = interpret_cron_expression(cron.expression)
        return result
    except ValueError as ve:
        raise CustomHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            status_msg="Bad Request",
            detail=str(ve)
        )
    except Exception as e:
        raise CustomHTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            status_msg="Internal Server Error",
            detail=str(e)
        )
