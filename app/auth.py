import hmac

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config import API_KEY


class APIKeyMiddleware(BaseHTTPMiddleware):
    """Reject requests missing a valid X-API-Key header.

    The /health route is exempted so Fly.io can probe it without credentials.
    If API_KEY is not configured the service denies every authenticated route
    (secure-by-default).
    """

    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/health":
            return await call_next(request)

        key = request.headers.get("X-API-Key", "")
        if not API_KEY or not hmac.compare_digest(key, API_KEY):
            return JSONResponse(
                status_code=403, content={"detail": "Unauthorized"}
            )

        return await call_next(request)
