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

def get_cron_trigger():
    """Create a cron trigger based on current frequency settings"""
    # Parse buy time from config (format: HH:MM)
    hour, minute = config.BUY_TIME.split(':')
    
    if config.ORDER_FREQUENCY == 'daily':
        # Create a cron trigger to execute daily at the specified time (UTC)
        return CronTrigger(
            hour=hour,
            minute=minute,
            timezone='UTC'
        )
    else:  # weekly
        # Get day of week (0-6 where 0=Monday)
        day_of_week_map = {
            'monday': 0,
            'tuesday': 1,
            'wednesday': 2,
            'thursday': 3,
            'friday': 4,
            'saturday': 5,
            'sunday': 6
        }
        day_of_week = day_of_week_map.get(config.WEEKLY_DAY.lower(), 0)  # Default to Monday (0)
        
        # Create a cron trigger to execute weekly on the specified day and time (UTC)
        return CronTrigger(
            day_of_week=day_of_week,
            hour=hour,
            minute=minute,
            timezone='UTC'
        )

def init_scheduler():
    """Initialize and start the scheduler for buys"""
    try:
        # Create a trigger based on current frequency settings
        trigger = get_cron_trigger()
        
        # Add the job to the scheduler
        scheduler.add_job(
            func=execute_daily_buy,
            trigger=trigger,
            id='buy_job',
            name=f'Execute {config.ORDER_FREQUENCY} {config.PRODUCT_ID} buy',
            replace_existing=True
        )
        
        # Start the scheduler
        scheduler.start()
        
        if config.ORDER_FREQUENCY == 'daily':
            logger.info(f"Scheduler started: Daily buy of {config.DAILY_AMOUNT} EUR of {config.PRODUCT_ID} at {config.BUY_TIME} UTC")
        else:
            logger.info(f"Scheduler started: Weekly buy of {config.DAILY_AMOUNT} EUR of {config.PRODUCT_ID} on {config.WEEKLY_DAY.capitalize()} at {config.BUY_TIME} UTC")
    except Exception as e:
        logger.error(f"Failed to initialize scheduler: {str(e)}")
        raise

def update_scheduler():
    """Update the scheduler with new settings"""
    try:
        # Only update if the scheduler is running
        if scheduler.running:
            logger.info("Updating scheduler with new settings")
            
            # Create a new trigger based on current frequency settings
            trigger = get_cron_trigger()
            
            # Update job name based on frequency
            job = scheduler.get_job('buy_job')
            if job:
                job.name = f'Execute {config.ORDER_FREQUENCY} {config.PRODUCT_ID} buy'
            
            # Reschedule the job with the new trigger
            scheduler.reschedule_job(
                'buy_job',
                trigger=trigger
            )
            
            if config.ORDER_FREQUENCY == 'daily':
                logger.info(f"Scheduler updated: Daily buy of {config.DAILY_AMOUNT} EUR of {config.PRODUCT_ID} at {config.BUY_TIME} UTC")
            else:
                logger.info(f"Scheduler updated: Weekly buy of {config.DAILY_AMOUNT} EUR of {config.PRODUCT_ID} on {config.WEEKLY_DAY.capitalize()} at {config.BUY_TIME} UTC")
            return True
        else:
            logger.warning("Scheduler is not running, cannot update")
            return False
    except Exception as e:
        logger.error(f"Failed to update scheduler: {str(e)}")
        raise

def get_next_run_time():
    """Get the next scheduled run time for the buy job"""
    try:
        job = scheduler.get_job('buy_job')
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

