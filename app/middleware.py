# ==============================================================================
# File: app/middleware.py
# Project: SuryaGharSathi (सूर्याघर साथी)
# Description: Day 13 - Production Observability & Request Timing Middleware.
#              Tracks per-request latency (in ms), injects correlation IDs (X-Request-ID),
#              and records structured request logs for observability.
# ==============================================================================

import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("observability")


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """
    Production middleware measuring end-to-end request latency and assigning
    unique correlation IDs for distributed tracing.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Extract or generate unique request identifier
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        start_time = time.perf_counter()

        # Attach request_id to request state for downstream handlers
        request.state.request_id = request_id

        # Process the downstream request
        response: Response = await call_next(request)

        # Compute total latency in milliseconds
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # Inject diagnostic headers into response
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-Ms"] = str(duration_ms)

        # Log structured request completion
        logger.info(
            f"[{request_id[:8]}] {request.method} {request.url.path} "
            f"-> Status {response.status_code} ({duration_ms} ms)"
        )

        return response
