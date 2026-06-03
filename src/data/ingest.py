import logging
import time
from src.config import MUTUAL_FUND_URLS
from src.data.scraper import fetch_scheme
from src.data.db import init_db, save_scheme

logger = logging.getLogger(__name__)

def run_ingestion():
    """
    Orchestrates the daily ingestion run:
    1. Initializes the SQLite DB if needed.
    2. Iterates over target Groww URLs.
    3. Fetches, parses, and upserts each scheme details.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    
    logger.info("Starting Daily Ingestion Routine...")
    init_db()
    
    success_count = 0
    failure_count = 0
    
    for url in MUTUAL_FUND_URLS:
        try:
            scheme = fetch_scheme(url)
            save_scheme(scheme)
            success_count += 1
            time.sleep(2) # Politeness delay
        except Exception as e:
            logger.error(f"Failed to ingest URL {url}: {e}", exc_info=True)
            failure_count += 1
            
    logger.info(f"Ingestion Finished. Successes: {success_count}, Failures: {failure_count}")
    
    if success_count > 0:
        try:
            from src.data.db import get_all_schemes
            from src.data.vector_store import index_schemes_in_vector_store
            schemes = get_all_schemes()
            index_schemes_in_vector_store(schemes)
            logger.info("Vector store updated successfully.")
        except Exception as e:
            logger.error(f"Failed to index schemes in vector store: {e}", exc_info=True)
            
    return success_count == len(MUTUAL_FUND_URLS)

if __name__ == "__main__":
    run_ingestion()
