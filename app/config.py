import os
import logging
from dotenv import load_dotenv, find_dotenv, set_key

# Set up logging
logger = logging.getLogger('coinbase_app.config')

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

# Admin credentials
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'password')

def validate_config():
    """Validate that all required configuration is present"""
    if not COINBASE_API_KEY or not COINBASE_API_SECRET:
        raise ValueError('Coinbase API credentials are required')
    
    if not PRODUCT_ID:
        raise ValueError('Product ID is required')
    
    if not DAILY_AMOUNT or DAILY_AMOUNT <= 0:
        raise ValueError('Daily amount must be greater than 0')

def update_settings(new_product_id=None, new_daily_amount=None, new_buy_time=None):
    """Update the application settings and save to .env file"""
    global PRODUCT_ID, DAILY_AMOUNT, BUY_TIME
    
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
