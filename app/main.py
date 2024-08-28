import time
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routers import interpret
from app.models.errors import ValidationErrorDetail, ValidationErrorResponse
from app.utils.custom_exception import CustomHTTPException
# from middlewares.rate_limit_middleware import RateLimitMiddleware
# from middlewares.logging_middleware import LoggingMiddleware
# from custom_logging import CustomizeLogger


app = FastAPI(title="Cron Expression Interpreter API")
# logger_config_path = Path("logging_config.json")
# logger = CustomizeLogger.make_logger(logger_config_path)

# app.add_middleware(LoggingMiddleware, custom_logger=logger)
# app.add_middleware(RateLimitMiddleware)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exception: RequestValidationError):
    errors = []
    for error in exception.errors():
        field = error["loc"][-1]
        msg = error["msg"]
        errors.append(ValidationErrorDetail(field=field, message=msg))
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ValidationErrorResponse(errors=errors).model_dump()
    )

@app.exception_handler(CustomHTTPException)
async def custom_http_exception_handler(
    request: Request, exception: CustomHTTPException
):
    return JSONResponse(
        status_code=exception.status_code,
        content=exception.detail
    )

app.include_router(interpret.router, prefix="/cron-expression-interpreter", tags=["Cron Expression Interpreter"])

@app.get("/")
def read_root():
    # logger.info("Starting Crontab Pattern Interpreter API")
    return {"message": "Welcome to the Cron Expression Interpreter API"}