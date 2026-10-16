import os
import secrets

# Database configuration: Default to local zero-dependency SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./legaltantra.db")

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Security configuration (fallback to generated ephemeral secrets in dev if not set)
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    if ENVIRONMENT == "production":
        raise RuntimeError("JWT_SECRET environment variable must be set in production mode.")
    JWT_SECRET = "dev-insecure-secret-key-legal-tantra-2026"

ENCRYPTION_KEY_RAW = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY_RAW:
    ENCRYPTION_KEY_RAW = "dev-insecure-32bytes-key-tantra"
ENCRYPTION_KEY = ENCRYPTION_KEY_RAW.encode()

# AI Provider configurations
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# AI Provider selection: "gemini", "openai", or "deterministic" fallback
if GEMINI_API_KEY:
    AI_PROVIDER = "gemini"
elif OPENAI_API_KEY:
    AI_PROVIDER = "openai"
else:
    AI_PROVIDER = "deterministic"

# Request timeouts for external APIs (seconds)
AI_REQUEST_TIMEOUT = int(os.getenv("AI_REQUEST_TIMEOUT", "12"))

# Rate Limiting configuration
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() in ("true", "1", "yes")
RATE_LIMIT_DEFAULT_LIMIT = int(os.getenv("RATE_LIMIT_DEFAULT_LIMIT", "60"))
RATE_LIMIT_DEFAULT_WINDOW = int(os.getenv("RATE_LIMIT_DEFAULT_WINDOW", "60"))
RATE_LIMIT_AI_LIMIT = int(os.getenv("RATE_LIMIT_AI_LIMIT", "20"))
RATE_LIMIT_AI_WINDOW = int(os.getenv("RATE_LIMIT_AI_WINDOW", "60"))

# Payload size limit configuration
MAX_JSON_BODY_SIZE = int(os.getenv("MAX_JSON_BODY_SIZE", str(1 * 1024 * 1024)))      # 1 MB
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", str(10 * 1024 * 1024)))          # 10 MB

# Directory configurations
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
