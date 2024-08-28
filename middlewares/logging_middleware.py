from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
import time
import uuid

class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, custom_logger):
        super().__init__(app)
        self.logger = custom_logger

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        request_id = str(uuid.uuid4())
        log = self.logger.bind(request_id=request_id)

        log.info(f"Request: {request.method} {request.url}")
        start_time = time.time()

        try:
            response = await call_next(request)
            time_taken = time.time() - start_time
            log.info(f"Response: {response.status_code} for {request.url} in {time_taken:.2f}s")
        except Exception as e:
            log.exception(f"Exception occurred while processing request: {e}")
            raise

        return response
