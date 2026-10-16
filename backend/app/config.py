import os

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:securepassword123@db:5432/legal_assistance"
)
JWT_SECRET = os.getenv(
    "JWT_SECRET", 
    "supersecretjwtkeychangeinproduction2026"
)
ENCRYPTION_KEY = os.getenv(
    "ENCRYPTION_KEY", 
    "32byteslongsecretkeyforaesencryption"
).encode()

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Directory configurations
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Pluggable configuration
# If API keys are empty, services default to mock/deterministic responses
AI_PROVIDER = "gemini" if GEMINI_API_KEY else ("openai" if OPENAI_API_KEY else "mock")
