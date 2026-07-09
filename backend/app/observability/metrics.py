from prometheus_client import Counter, Gauge, Histogram


HTTP_REQUESTS_TOTAL = Counter(
    "task_api_http_requests_total",
    "Общее количество HTTP-запросов",
    ["method", "path", "status"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "task_api_http_request_duration_seconds",
    "Время выполнения HTTP-запросов в секундах",
    ["method", "path"],
)

HTTP_REQUESTS_IN_PROGRESS = Gauge(
    "task_api_http_requests_in_progress",
    "Количество HTTP-запросов, выполняющихся сейчас",
    ["method"],
)

HTTP_ERRORS_TOTAL = Counter(
    "task_api_http_errors_total",
    "Общее количество HTTP-ошибок",
    ["method", "path", "status"],
)