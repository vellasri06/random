import os
from typing import List

# Simple environment config accessors

API_TITLE = os.getenv("API_TITLE", "Automated MoM Generator")

# CSV of allowed origins or '*' for all
CORS_ALLOW_ORIGINS_RAW = os.getenv("CORS_ALLOW_ORIGINS", "*")
CORS_ALLOW_ORIGINS: List[str]
if CORS_ALLOW_ORIGINS_RAW.strip() == "*":
    CORS_ALLOW_ORIGINS = ["*"]
else:
    CORS_ALLOW_ORIGINS = [o.strip() for o in CORS_ALLOW_ORIGINS_RAW.split(",") if o.strip()]

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.2"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

GENERATED_PDFS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "generated_pdfs"))
os.makedirs(GENERATED_PDFS_DIR, exist_ok=True)
