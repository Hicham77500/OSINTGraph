"""Local session auth middleware — optional for localhost dev."""
import os

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

PUBLIC_PATHS = {"/health", "/docs", "/openapi.json", "/redoc"}


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if os.getenv("OSINTGRAPH_AUTH_DISABLED", "true").lower() == "true":
            request.state.actor = "local-analyst"
            return await call_next(request)

        if request.url.path in PUBLIC_PATHS or request.url.path.startswith("/docs"):
            return await call_next(request)

        token = request.headers.get("X-OSINTGraph-Session")
        expected = os.getenv("OSINTGRAPH_SESSION_SECRET", "")
        if not expected or token != expected:
            return JSONResponse({"detail": "Unauthorized"}, status_code=401)

        request.state.actor = "authenticated-analyst"
        return await call_next(request)
