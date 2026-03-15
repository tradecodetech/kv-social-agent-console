import os

# Load .env file if present (python-dotenv)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed — rely on real environment variables

# ===========================================================
# KV Systems Agent — Configuration
# All values are read from environment variables.
# Copy .env.example to .env and fill in your secrets.
# ===========================================================

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.85"))

# Agent behavior
MAX_GENERATION_RETRIES = int(os.getenv("MAX_GENERATION_RETRIES", "6"))

# Facebook Graph API version
FB_GRAPH_VERSION = os.getenv("FB_GRAPH_VERSION", "v19.0")

# Logging
LOG_DB_PATH = os.getenv("LOG_DB_PATH", "memory.db")
CSV_EXPORT_PATH = os.getenv("CSV_EXPORT_PATH", "kv_agent_analytics.csv")

# Pages config file
PAGES_JSON_PATH = os.getenv("PAGES_JSON_PATH", "pages.json")

# Validate required keys on import
if not OPENAI_API_KEY:
    raise RuntimeError(
        "OPENAI_API_KEY is not set.\n"
        "Add it to a .env file or set it as an environment variable.\n"
        "See .env.example for reference."
    )
