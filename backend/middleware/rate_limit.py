"""Simple in-memory rate limiter for transform endpoints."""
import os
import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

WINDOW_SEC = 60
DEFAULT_LIMIT = 30


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._hits: dict[str, list[float]] = defaultdict(list)
        self._limit = int(os.getenv("TRANSFORM_RATE_LIMIT", str(DEFAULT_LIMIT)))

    async def dispatch(self, request: Request, call_next):
        if not request.url.path.startswith("/transforms/run"):
            return await call_next(request)

        client = request.client.host if request.client else "unknown"
        now = time.time()
        window_start = now - WINDOW_SEC
        self._hits[client] = [t for t in self._hits[client] if t > window_start]

        if len(self._hits[client]) >= self._limit:
            return JSONResponse(
                {"detail": "Rate limit exceeded for transforms"},
                status_code=429,
            )

        self._hits[client].append(now)
        return await call_next(request)
