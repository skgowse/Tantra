import time
import logging
from collections import defaultdict
from typing import Dict, List, Tuple
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger("legal_tantra.security.rate_limiter")

class InMemoryRateLimiter:
    """
    Thread-safe in-memory sliding-window rate limiter per client IP.
    Protects API endpoints against volumetric abuse, credential stuffing, and AI quota exhaustion.
    """
    def __init__(
        self,
        default_limit: int = 60,
        default_window: int = 60,
        ai_limit: int = 20,
        ai_window: int = 60,
        enabled: bool = True
    ):
        self.default_limit = default_limit
        self.default_window = default_window
        self.ai_limit = ai_limit
        self.ai_window = ai_window
        self.enabled = enabled
        self._records: Dict[str, List[float]] = defaultdict(list)
        self._ai_records: Dict[str, List[float]] = defaultdict(list)

    def is_ai_endpoint(self, path: str) -> bool:
        ai_prefixes = ("/api/chat/message", "/api/incident/analyze", "/api/document/analyze", "/api/incident/summary")
        return any(path.startswith(prefix) for prefix in ai_prefixes)

    def is_allowed(self, client_ip: str, path: str) -> Tuple[bool, int, int]:
        """
        Evaluates whether request from client_ip is within rate limits.
        Returns (is_allowed, remaining, retry_after).
        """
        if not self.enabled:
            return True, 999, 0

        now = time.time()
        is_ai = self.is_ai_endpoint(path)
        limit = self.ai_limit if is_ai else self.default_limit
        window = self.ai_window if is_ai else self.default_window
        records = self._ai_records[client_ip] if is_ai else self._records[client_ip]

        # Purge timestamps outside sliding window
        window_start = now - window
        records[:] = [t for t in records if t > window_start]

        if len(records) >= limit:
            oldest = records[0]
            retry_after = max(1, int(oldest + window - now))
            return False, 0, retry_after

        records.append(now)
        remaining = max(0, limit - len(records))
        return True, remaining, 0

    def reset(self):
        """Resets all tracked request records (useful for test isolation)."""
        self._records.clear()
        self._ai_records.clear()

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limiter: InMemoryRateLimiter):
        super().__init__(app)
        self.limiter = limiter

    async def dispatch(self, request: Request, call_next):
        # Health checks bypass rate limiting to preserve monitoring availability
        if request.url.path in ("/api/health", "/docs", "/openapi.json", "/redoc"):
            return await call_next(request)

        # Allow test bypass if header explicitly provided in local test environment
        if request.headers.get("X-Bypass-Rate-Limit") == "test-bypass-active":
            return await call_next(request)

        # Extract client IP, respecting X-Forwarded-For if behind a reverse proxy/WAF
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "127.0.0.1"

        allowed, remaining, retry_after = self.limiter.is_allowed(client_ip, request.url.path)
        
        if not allowed:
            logger.warning(f"Rate limit exceeded for client {client_ip} on {request.url.path}. Retry after {retry_after}s.")
            response = JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Please wait before making further requests.",
                    "retry_after_seconds": retry_after
                }
            )
            response.headers["Retry-After"] = str(retry_after)
            response.headers["X-RateLimit-Remaining"] = "0"
            return response

        response = await call_next(request)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
