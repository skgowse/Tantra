from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware that enforces OWASP-recommended HTTP response security headers.
    Protects against MIME-sniffing, clickjacking, cross-site scripting (XSS),
    and unauthorized framing.
    """
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        
        # Prevent MIME-type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Prevent clickjacking / framing
        response.headers["X-Frame-Options"] = "DENY"
        
        # Enable browser XSS filter
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Control referrer leakage
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Restrict dangerous browser features
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Content Security Policy (allows local API connectivity and safe frontend asset loading)
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline'",
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: https:",
            "connect-src 'self' http://localhost:* http://127.0.0.1:* ws://localhost:* ws://127.0.0.1:*",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'"
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)
        
        # If connection is HTTPS or behind HTTPS proxy, add HSTS
        if request.url.scheme == "https" or request.headers.get("x-forwarded-proto") == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
            
        return response
