import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger("legal_tantra.security.payload_limiter")

DEFAULT_MAX_JSON_SIZE = 1 * 1024 * 1024  # 1 MB
DEFAULT_MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB

class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware that enforces maximum request body sizes.
    Rejects oversized requests with 413 Payload Too Large before processing,
    mitigating Denial of Service (DoS) and buffer exhaustion attacks.
    """
    def __init__(self, app, max_json_size: int = DEFAULT_MAX_JSON_SIZE, max_upload_size: int = DEFAULT_MAX_UPLOAD_SIZE):
        super().__init__(app)
        self.max_json_size = max_json_size
        self.max_upload_size = max_upload_size

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        limit = self.max_upload_size if path.startswith("/api/document/") else self.max_json_size

        content_length = request.headers.get("content-length")
        if content_length:
            try:
                length = int(content_length)
                if length > limit:
                    logger.warning(f"Rejected oversized request from {request.client.host if request.client else 'unknown'}: {length} bytes > {limit} bytes limit.")
                    return JSONResponse(
                        status_code=413,
                        content={
                            "detail": f"Payload too large. Maximum allowed size is {limit} bytes ({limit // (1024*1024)} MB).",
                            "received_bytes": length,
                            "limit_bytes": limit
                        }
                    )
            except ValueError:
                return JSONResponse(status_code=400, content={"detail": "Invalid Content-Length header."})

        return await call_next(request)
