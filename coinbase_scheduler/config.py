import os
import logging
from dotenv import load_dotenv, find_dotenv, set_key

# Set up logging
logger = logging.getLogger('coinbase_scheduler.config')

# Load environment variables
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

# Coinbase API settings
COINBASE_API_KEY = os.getenv('COINBASE_API_KEY')
COINBASE_API_SECRET = os.getenv('COINBASE_API_SECRET')

# Trading settings
PRODUCT_ID = os.getenv('PRODUCT_ID', 'BTC-EUR')
DAILY_AMOUNT = float(os.getenv('DAILY_AMOUNT', '30'))
BUY_TIME = os.getenv('BUY_TIME', '08:00')  # UTC time
ORDER_FREQUENCY = os.getenv('ORDER_FREQUENCY', 'daily')  # 'daily' or 'weekly'
WEEKLY_DAY = os.getenv('WEEKLY_DAY', 'monday')  # Day of the week for weekly orders

def validate_config():
    """Validate that all required configuration is present"""
    if not COINBASE_API_KEY or not COINBASE_API_SECRET:
        raise ValueError('Coinbase API credentials are required')
    
    if not PRODUCT_ID:
        raise ValueError('Product ID is required')
    
    if not DAILY_AMOUNT or DAILY_AMOUNT <= 0:
        raise ValueError('Daily amount must be greater than 0')

def update_settings(new_product_id=None, new_daily_amount=None, new_buy_time=None, 
                new_order_frequency=None, new_weekly_day=None):
    """Update the application settings and save to .env file"""
    global PRODUCT_ID, DAILY_AMOUNT, BUY_TIME, ORDER_FREQUENCY, WEEKLY_DAY
    
    updated = False
    
    # Update product ID if provided
    if new_product_id and new_product_id != PRODUCT_ID:
        logger.info(f"Updating product ID from {PRODUCT_ID} to {new_product_id}")
        PRODUCT_ID = new_product_id
        set_key(dotenv_path, 'PRODUCT_ID', new_product_id)
        updated = True
    
    # Update daily amount if provided
    if new_daily_amount is not None:
        try:
            new_amount = float(new_daily_amount)
            if new_amount != DAILY_AMOUNT:
                logger.info(f"Updating daily amount from {DAILY_AMOUNT} to {new_amount}")
                DAILY_AMOUNT = new_amount
                set_key(dotenv_path, 'DAILY_AMOUNT', str(new_amount))
                updated = True
        except ValueError:
            logger.error(f"Invalid daily amount value: {new_daily_amount}")
            raise ValueError("Daily amount must be a valid number")
    
    # Update buy time if provided
    if new_buy_time and new_buy_time != BUY_TIME:
        # Validate time format (HH:MM)
        if not validate_time_format(new_buy_time):
            logger.error(f"Invalid time format: {new_buy_time}")
            raise ValueError("Buy time must be in HH:MM format")
        
        logger.info(f"Updating buy time from {BUY_TIME} to {new_buy_time}")
        BUY_TIME = new_buy_time
        set_key(dotenv_path, 'BUY_TIME', new_buy_time)
        updated = True
    
    # Update order frequency if provided
    if new_order_frequency and new_order_frequency != ORDER_FREQUENCY:
        if new_order_frequency not in ['daily', 'weekly']:
            logger.error(f"Invalid order frequency: {new_order_frequency}")
            raise ValueError("Order frequency must be 'daily' or 'weekly'")
        
        logger.info(f"Updating order frequency from {ORDER_FREQUENCY} to {new_order_frequency}")
        ORDER_FREQUENCY = new_order_frequency
        set_key(dotenv_path, 'ORDER_FREQUENCY', new_order_frequency)
        updated = True
    
    # Update weekly day if provided
    if new_weekly_day and new_weekly_day != WEEKLY_DAY:
        valid_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        if new_weekly_day.lower() not in valid_days:
            logger.error(f"Invalid day of week: {new_weekly_day}")
            raise ValueError("Day of week must be a valid day (Monday-Sunday)")
        
        new_weekly_day = new_weekly_day.lower()
        logger.info(f"Updating weekly day from {WEEKLY_DAY} to {new_weekly_day}")
        WEEKLY_DAY = new_weekly_day
        set_key(dotenv_path, 'WEEKLY_DAY', new_weekly_day)
        updated = True
    
    return updated

def validate_time_format(time_str):
    """Validate that a string is in HH:MM format"""
    try:
        hour, minute = time_str.split(':')
        hour = int(hour)
        minute = int(minute)
        return 0 <= hour < 24 and 0 <= minute < 60
    except (ValueError, TypeError):
        return False
