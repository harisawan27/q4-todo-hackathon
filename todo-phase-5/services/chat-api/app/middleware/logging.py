"""Request/response logging middleware with trace_id propagation."""

import logging
import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = logging.getLogger("chat-api")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        trace_id = request.headers.get("traceparent", str(uuid.uuid4()))
        request.state.trace_id = trace_id

        start_time = time.time()
        response = await call_next(request)
        duration_ms = (time.time() - start_time) * 1000

        logger.info(
            f"{request.method} {request.url.path} {response.status_code} {duration_ms:.1f}ms",
            extra={"service": "chat-api", "trace_id": trace_id},
        )
        response.headers["X-Trace-Id"] = trace_id
        return response
