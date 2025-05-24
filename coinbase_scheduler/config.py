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
AMOUNT = float(os.getenv('AMOUNT', '30'))
BUY_TIME = os.getenv('BUY_TIME', '08:00')  # UTC time
ORDER_FREQUENCY = os.getenv('ORDER_FREQUENCY', 'daily')  # 'daily', 'weekly', or 'monthly'
WEEKLY_DAY = os.getenv('WEEKLY_DAY', 'monday')  # Day of the week for weekly orders
MONTHLY_DAY = int(os.getenv('MONTHLY_DAY', '1'))  # Day of the month (1-28) for monthly orders

# Telegram settings
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TELEGRAM_NOTIFICATIONS_ENABLED = os.getenv('TELEGRAM_NOTIFICATIONS_ENABLED', 'true').lower() == 'true'

def validate_config():
    """Validate that all required configuration is present"""
    if not COINBASE_API_KEY or not COINBASE_API_SECRET:
        raise ValueError('Coinbase API credentials are required')
    
    if not PRODUCT_ID:
        raise ValueError('Product ID is required')
    
    if not AMOUNT or AMOUNT <= 0:
        raise ValueError('Amount must be greater than 0')
    
    if ORDER_FREQUENCY == 'monthly':
        if MONTHLY_DAY < 1 or MONTHLY_DAY > 28:
            raise ValueError('Monthly day must be between 1 and 28')
    
    # Check Telegram configuration if notifications are enabled
    if TELEGRAM_NOTIFICATIONS_ENABLED:
        if not TELEGRAM_BOT_TOKEN:
            logger.warning('Telegram notifications are enabled but bot token is missing')
        if not TELEGRAM_CHAT_ID:
            logger.warning('Telegram notifications are enabled but chat ID is missing')

def update_settings(new_product_id=None, new_amount=None, new_buy_time=None, 
                new_order_frequency=None, new_weekly_day=None, new_monthly_day=None,
                new_telegram_enabled=None, new_telegram_bot_token=None, new_telegram_chat_id=None):
    """Update the application settings and save to .env file"""
    global PRODUCT_ID, AMOUNT, BUY_TIME, ORDER_FREQUENCY, WEEKLY_DAY, MONTHLY_DAY, TELEGRAM_NOTIFICATIONS_ENABLED, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
    
    updated = False
    
    # Update product ID if provided
    if new_product_id and new_product_id != PRODUCT_ID:
        logger.info(f"Updating product ID from {PRODUCT_ID} to {new_product_id}")
        PRODUCT_ID = new_product_id
        set_key(dotenv_path, 'PRODUCT_ID', new_product_id)
        updated = True
    
    # Update amount if provided
    if new_amount is not None:
        try:
            amount_value = float(new_amount)
            if amount_value != AMOUNT:
                logger.info(f"Updating amount from {AMOUNT} to {amount_value}")
                AMOUNT = amount_value
                set_key(dotenv_path, 'AMOUNT', str(amount_value))
                updated = True
        except ValueError:
            logger.error(f"Invalid amount value: {new_amount}")
            raise ValueError("Amount must be a valid number")
    
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
        if new_order_frequency not in ['daily', 'weekly', 'monthly']:
            logger.error(f"Invalid order frequency: {new_order_frequency}")
            raise ValueError("Order frequency must be 'daily', 'weekly', or 'monthly'")
        
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
    
    # Update monthly day if provided
    if new_monthly_day is not None:
        try:
            day = int(new_monthly_day)
            if day < 1 or day > 28:
                logger.error(f"Invalid monthly day: {new_monthly_day}")
                raise ValueError("Monthly day must be between 1 and 28")
            
            if day != MONTHLY_DAY:
                logger.info(f"Updating monthly day from {MONTHLY_DAY} to {day}")
                MONTHLY_DAY = day
                set_key(dotenv_path, 'MONTHLY_DAY', str(day))
                updated = True
        except ValueError:
            logger.error(f"Invalid monthly day value: {new_monthly_day}")
            raise ValueError("Monthly day must be a valid integer between 1 and 28")
    
    # Update Telegram notification enabled if provided
    if new_telegram_enabled is not None:
        try:
            new_enabled = str(new_telegram_enabled).lower() == 'true'
            if new_enabled != TELEGRAM_NOTIFICATIONS_ENABLED:
                logger.info(f"Updating Telegram notifications enabled from {TELEGRAM_NOTIFICATIONS_ENABLED} to {new_enabled}")
                TELEGRAM_NOTIFICATIONS_ENABLED = new_enabled
                set_key(dotenv_path, 'TELEGRAM_NOTIFICATIONS_ENABLED', str(new_enabled).lower())
                updated = True
        except Exception as e:
            logger.error(f"Invalid Telegram notifications enabled value: {new_telegram_enabled}")
            raise ValueError("Telegram notifications enabled must be a boolean")
    
    # Update Telegram bot token if provided
    if new_telegram_bot_token and new_telegram_bot_token != TELEGRAM_BOT_TOKEN:
        logger.info("Updating Telegram bot token")
        TELEGRAM_BOT_TOKEN = new_telegram_bot_token
        set_key(dotenv_path, 'TELEGRAM_BOT_TOKEN', new_telegram_bot_token)
        updated = True
    
    # Update Telegram chat ID if provided
    if new_telegram_chat_id and new_telegram_chat_id != TELEGRAM_CHAT_ID:
        logger.info("Updating Telegram chat ID")
        TELEGRAM_CHAT_ID = new_telegram_chat_id
        set_key(dotenv_path, 'TELEGRAM_CHAT_ID', new_telegram_chat_id)
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
