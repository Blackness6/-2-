import time
from collections.abc import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.observability.metrics import (
    HTTP_ERRORS_TOTAL,
    HTTP_REQUEST_DURATION_SECONDS,
    HTTP_REQUESTS_IN_PROGRESS,
    HTTP_REQUESTS_TOTAL,
)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        method = request.method

        # Не считаем запрос Prometheus к самому /metrics.
        if request.url.path == "/metrics":
            return await call_next(request)

        HTTP_REQUESTS_IN_PROGRESS.labels(method=method).inc()
        start_time = time.perf_counter()

        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
            return response

        finally:
            duration_seconds = time.perf_counter() - start_time

            route = request.scope.get("route")
            path = getattr(route, "path", request.url.path)

            HTTP_REQUESTS_TOTAL.labels(
                method=method,
                path=path,
                status=str(status_code),
            ).inc()

            HTTP_REQUEST_DURATION_SECONDS.labels(
                method=method,
                path=path,
            ).observe(duration_seconds)

            if status_code >= 400:
                HTTP_ERRORS_TOTAL.labels(
                    method=method,
                    path=path,
                    status=str(status_code),
                ).inc()

            HTTP_REQUESTS_IN_PROGRESS.labels(method=method).dec()