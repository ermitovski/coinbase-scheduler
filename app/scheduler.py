import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app import config
from app.trading import execute_daily_buy

# Set up logging
logger = logging.getLogger('coinbase_app.scheduler')

# Initialize the scheduler
scheduler = BackgroundScheduler()

def init_scheduler():
    """Initialize and start the scheduler for daily buys"""
    try:
        # Parse buy time from config (format: HH:MM)
        hour, minute = config.BUY_TIME.split(':')
        
        # Create a cron trigger to execute daily at the specified time (UTC)
        trigger = CronTrigger(
            hour=hour,
            minute=minute,
            timezone='UTC'
        )
        
        # Add the job to the scheduler
        scheduler.add_job(
            func=execute_daily_buy,
            trigger=trigger,
            id='daily_buy_job',
            name='Execute daily BTC-EUR buy',
            replace_existing=True
        )
        
        # Start the scheduler
        scheduler.start()
        logger.info(f"Scheduler started: Daily buy of {config.DAILY_AMOUNT} EUR of {config.PRODUCT_ID} at {config.BUY_TIME} UTC")
    except Exception as e:
        logger.error(f"Failed to initialize scheduler: {str(e)}")
        raise

def get_next_run_time():
    """Get the next scheduled run time for the daily buy job"""
    try:
        job = scheduler.get_job('daily_buy_job')
        if job and job.next_run_time:
            return job.next_run_time.isoformat()
        return None
    except Exception as e:
        logger.error(f"Failed to get next run time: {str(e)}")
        return None

def manual_buy():
    """Manually trigger a buy operation"""
    try:
        result = execute_daily_buy()
        logger.info("Manual buy executed successfully")
        return result
    except Exception as e:
        logger.error(f"Manual buy failed: {str(e)}")
        raise
