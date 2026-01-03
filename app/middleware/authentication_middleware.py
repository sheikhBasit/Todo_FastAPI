from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class AuthenticationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Exclude specific paths from authentication
        excluded_paths = ["/auth/register", "/auth/login", "/db-status","/","/docs","/redoc","/openapi.json"]
        if request.url.path in excluded_paths:
            return await call_next(request)

        # Check for an Authorization header
        if "Authorization" not in request.headers:
            return Response("Unauthorized", status_code=401)
        return await call_next(request)