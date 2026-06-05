import os
import logging
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.services.orchestrator import ask_question
from src.data.db import get_all_schemes, get_connection
from src.config import LLM_PROVIDER, LLM_MODEL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Mutual Fund FAQ Assistant API", version="1.0.0")

# Enable CORS for local testing/development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    import threading
    from src.data.scheduler import start_scheduler
    # Start the scheduler in a daemon thread so it doesn't block FastAPI startup
    scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
    scheduler_thread.start()
    logger.info("Daemon scheduler thread started.")

# Static file paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_HTML_PATH = os.path.join(CURRENT_DIR, "index.html")

class QueryRequest(BaseModel):
    query: str

@app.get("/")
def read_root():
    """Serves the static frontend index.html."""
    if not os.path.exists(INDEX_HTML_PATH):
        raise HTTPException(status_code=404, detail="Frontend index.html not found.")
    return FileResponse(INDEX_HTML_PATH)

@app.get("/api/v1/schemes")
def get_schemes():
    """Lists the mutual fund schemes currently in the database."""
    try:
        schemes = get_all_schemes()
        return [{"name": s.scheme_name, "url": s.url, "nav": s.nav} for s in schemes]
    except Exception as e:
        logger.error(f"Error fetching schemes: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch schemes from database.")

@app.get("/api/v1/stats")
def get_stats():
    """Returns database facts and RAG system statistics."""
    try:
        schemes = get_all_schemes()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM managers")
        manager_count = cursor.fetchone()[0]
        conn.close()
        
        return {
            "schemes_count": len(schemes),
            "managers_count": manager_count,
            "llm_provider": LLM_PROVIDER,
            "llm_model": LLM_MODEL
        }
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch statistics.")

@app.post("/api/v1/chat")
def chat_endpoint(payload: QueryRequest):
    """Executes user queries via the RAG query orchestration pipeline."""
    if not payload.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    
    try:
        response = ask_question(payload.query)
        return response
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate response: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0" if os.environ.get("PORT") else "127.0.0.1"
    uvicorn.run(app, host=host, port=port)
