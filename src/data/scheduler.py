import time
import logging
from datetime import datetime, timedelta
from src.data.ingest import run_ingestion

logger = logging.getLogger(__name__)

def start_scheduler():
    """
    Starts a blocking loop that executes the mutual fund ingestion routine
    daily at 10:00 AM IST.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    
    logger.info("Initializing daily ingestion scheduler (scheduled for 10:00 AM IST)...")
    
    # Run immediate ingestion on boot to ensure database availability
    logger.info("Running initial ingestion on startup...")
    run_ingestion()
    
    try:
        while True:
            # Calculate delay until next 10:00 AM IST (system local time is IST)
            now = datetime.now()
            target = now.replace(hour=10, minute=0, second=0, microsecond=0)
            
            # If 10:00 AM has already passed today, set next run to tomorrow
            if now >= target:
                target += timedelta(days=1)
                
            delay_seconds = (target - now).total_seconds()
            logger.info(f"Next scheduled ingestion run at: {target.strftime('%Y-%m-%d %H:%M:%S')} (in {delay_seconds:.1f} seconds)")
            
            # Sleep until the target time
            time.sleep(delay_seconds)
            
            logger.info("Triggering scheduled daily ingestion at 10:00 AM...")
            run_ingestion()
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user.")
    except Exception as e:
        logger.critical(f"Scheduler crashed: {e}", exc_info=True)

if __name__ == "__main__":
    start_scheduler()
