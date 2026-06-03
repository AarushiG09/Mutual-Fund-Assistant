import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# LLM Config
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.1-70b-versatile")

# Storage Configuration
SQLITE_DB_PATH = os.path.join(BASE_DIR, os.getenv("SQLITE_DB_PATH", "data/mutual_funds.db"))
CHROMA_DB_PATH = os.path.join(BASE_DIR, os.getenv("CHROMA_DB_PATH", "data/chroma_db"))

# Ensure directory for databases exists
os.makedirs(os.path.dirname(SQLITE_DB_PATH), exist_ok=True)
os.makedirs(CHROMA_DB_PATH, exist_ok=True)

# Embedding Model
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")

# Ingestion settings
DATA_INGESTION_INTERVAL_HOURS = int(os.getenv("DATA_INGESTION_INTERVAL_HOURS", "24"))

# Target URLs for HDFC Mutual Funds on Groww
MUTUAL_FUND_URLS = [
    "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth",
    "https://groww.in/mutual-funds/hdfc-defence-fund-direct-growth"
]

# Standard request headers to bypass security/bot checks
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
