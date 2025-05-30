import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from coinbase_scheduler import config
from coinbase_scheduler.trading import execute_buy, check_pending_orders

# Set up logging
logger = logging.getLogger('coinbase_scheduler.scheduler')

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
    elif config.ORDER_FREQUENCY == 'weekly':
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
    else:  # monthly
        # Create a cron trigger to execute monthly on the specified day and time (UTC)
        # Note: Using day instead of day_of_week for monthly scheduling
        return CronTrigger(
            day=config.MONTHLY_DAY,
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
            func=execute_buy,
            trigger=trigger,
            id='buy_job',
            name=f'Execute {config.ORDER_FREQUENCY} {config.PRODUCT_ID} buy',
            replace_existing=True
        )
        
        # Don't add the check_orders_job here - it will be added dynamically when orders are placed
        
        # Start the scheduler
        scheduler.start()
        
        if config.ORDER_FREQUENCY == 'daily':
            logger.info(f"Scheduler started: Daily buy of {config.AMOUNT} EUR of {config.PRODUCT_ID} at {config.BUY_TIME} UTC")
        elif config.ORDER_FREQUENCY == 'weekly':
            logger.info(f"Scheduler started: Weekly buy of {config.AMOUNT} EUR of {config.PRODUCT_ID} on {config.WEEKLY_DAY.capitalize()} at {config.BUY_TIME} UTC")
        else:  # monthly
            logger.info(f"Scheduler started: Monthly buy of {config.AMOUNT} EUR of {config.PRODUCT_ID} on day {config.MONTHLY_DAY} at {config.BUY_TIME} UTC")
        
        logger.info("Order status checking will be scheduled dynamically when orders are placed")
        
        # Check if there are any pending orders from previous runs
        from coinbase_scheduler.trading import get_pending_orders
        if get_pending_orders():
            logger.info(f"Found {len(get_pending_orders())} pending orders from previous run")
            start_order_check_job()
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
                logger.info(f"Scheduler updated: Daily buy of {config.AMOUNT} EUR of {config.PRODUCT_ID} at {config.BUY_TIME} UTC")
            elif config.ORDER_FREQUENCY == 'weekly':
                logger.info(f"Scheduler updated: Weekly buy of {config.AMOUNT} EUR of {config.PRODUCT_ID} on {config.WEEKLY_DAY.capitalize()} at {config.BUY_TIME} UTC")
            else:  # monthly
                logger.info(f"Scheduler updated: Monthly buy of {config.AMOUNT} EUR of {config.PRODUCT_ID} on day {config.MONTHLY_DAY} at {config.BUY_TIME} UTC")
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

def get_next_check_time():
    """Get the next scheduled run time for the order check job"""
    try:
        job = scheduler.get_job('check_orders_job')
        if job and job.next_run_time:
            return job.next_run_time.isoformat()
        return None
    except Exception as e:
        logger.error(f"Failed to get next check time: {str(e)}")
        return None

def start_order_check_job():
    """Start the job to check pending orders every 5 minutes"""
    try:
        # Check if job already exists
        if scheduler.get_job('check_orders_job'):
            logger.debug("Order check job already exists")
            return
            
        # Add the job to check pending orders every 5 minutes
        scheduler.add_job(
            func=check_pending_orders,
            trigger=CronTrigger(minute='*/5', timezone='UTC'),
            id='check_orders_job',
            name='Check pending orders status',
            replace_existing=True
        )
        logger.info("Started order status checking job (every 5 minutes)")
    except Exception as e:
        logger.error(f"Failed to start order check job: {str(e)}")

def stop_order_check_job():
    """Stop the job that checks pending orders"""
    try:
        job = scheduler.get_job('check_orders_job')
        if job:
            scheduler.remove_job('check_orders_job')
            logger.info("Stopped order status checking job")
        else:
            logger.debug("Order check job was not running")
    except Exception as e:
        logger.error(f"Failed to stop order check job: {str(e)}")

def manual_buy(amount=None):
    """
    Manually trigger a buy operation
    
    Args:
        amount (float, optional): Custom amount to use for this buy. Defaults to None.
        
    Returns:
        dict: Result of the buy operation
    """
    try:
        result = execute_buy(amount=amount)
        logger.info("Manual buy executed successfully")
        return result
    except Exception as e:
        logger.error(f"Manual buy failed: {str(e)}")
        raise
