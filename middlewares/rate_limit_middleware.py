from fastapi import  Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime
from collections import defaultdict
from typing import Dict, List


class RateLimitMiddleware(BaseHTTPMiddleware):
    RATE_LIMIT = 100
    TIME_WINDOW = 60

    def __init__(self, app):
        super().__init__(app)
        self.rate_limit_records: Dict[str, List[float]] = defaultdict(List[float])

    async def dispatch(
        self, request: Request, call_next
    ):
        client_ip = request.client.host
        current_time = datetime.now().timestamp()

        # Record the current request timestamp
        self.rate_limit_records[client_ip].append(current_time)

        # Filter out timestamps that are outside the time window
        self.rate_limit_records[client_ip] = [
            timestamp for timestamp in self.rate_limit_records[client_ip]
            if current_time - timestamp <= self.TIME_WINDOW
        ]

        # Check if the number of requests exceeds the rate limit
        if len(self.rate_limit_records[client_ip]) > self.RATE_LIMIT:
            return JSONResponse(
                content={"detail": "Rate limit exceeded"},
                status_code=status.HTTP_429_TOO_MANY_REQUESTS
            )

        response = await call_next(request)
        return  response