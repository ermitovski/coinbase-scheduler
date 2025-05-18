import logging
import time
import signal
import sys
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('coinbase_scheduler')

# Load environment variables
load_dotenv()

# Import scheduler components
from app.scheduler import scheduler, init_scheduler
from app import config

# Signal handler for graceful shutdown
def handle_shutdown(signum, frame):
    logger.info("Received shutdown signal, shutting down scheduler...")
    if scheduler.running:
        scheduler.shutdown()
    sys.exit(0)

def main():
    """Main function to run the scheduler process"""
    try:
        # Set up signal handlers
        signal.signal(signal.SIGINT, handle_shutdown)
        signal.signal(signal.SIGTERM, handle_shutdown)
        
        logger.info("Starting scheduler process...")
        
        # Validate configuration
        config.validate_config()
        
        # Initialize and start scheduler
        init_scheduler()
        
        logger.info("Scheduler started successfully")
        
        # Keep the process running until a signal is received
        while True:
            time.sleep(60)  # Sleep to reduce CPU usage
            
    except Exception as e:
        logger.error(f"Error in scheduler process: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
