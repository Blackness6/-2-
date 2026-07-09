import logging 
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()

        response = await call_next(request)

        duration = (time.perf_counter() - start_time) * 1000

        logger.info(
            "%s %s -> %d (%.2f ms)",
            request.method,
            request.url.path,
            response.status_code,
            duration,
        )   

        return response