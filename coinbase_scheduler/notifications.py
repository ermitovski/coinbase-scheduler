import os
import logging
import requests
from urllib.parse import quote

# Set up logging
logger = logging.getLogger('coinbase_scheduler.notifications')

# Telegram configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TELEGRAM_NOTIFICATIONS_ENABLED = os.getenv('TELEGRAM_NOTIFICATIONS_ENABLED', 'true').lower() == 'true'

def send_telegram_notification(message):
    """
    Send a notification message via Telegram using the requests library.
    
    Args:
        message (str): The message to send
        
    Returns:
        bool: True if the message was sent successfully, False otherwise
    """
    if not TELEGRAM_NOTIFICATIONS_ENABLED:
        logger.info("Telegram notifications are disabled")
        return False
        
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram bot token or chat ID not configured")
        return False
        
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        
        # Prepare the request data
        data = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'Markdown'
        }
        
        # Send the request
        response = requests.post(url, data=data)
        
        # Check if request was successful
        if response.status_code == 200:
            logger.info("Telegram notification sent successfully")
            return True
        else:
            logger.error(f"Failed to send Telegram notification. Status code: {response.status_code}, Response: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to send Telegram notification: {str(e)}")
        return False

def format_order_notification(transaction):
    """
    Format an order notification message.
    
    Args:
        transaction (dict): Transaction details
        
    Returns:
        str: Formatted message
    """
    if transaction['status'] == 'Success':
        message = (
            f"🎉 *Coinbase Order Placed Successfully*\n\n"
            f"• *Product*: `{transaction['product_id']}`\n"
            f"• *Amount*: `{transaction['amount']} EUR`\n"
            f"• *Price*: `{transaction['price']}`\n"
            f"• *Order ID*: `{transaction['order_id']}`\n"
            f"• *Time*: `{transaction['timestamp']}`"
        )
    else:
        message = (
            f"❌ *Coinbase Order Failed*\n\n"
            f"• *Product*: `{transaction['product_id']}`\n"
            f"• *Amount*: `{transaction['amount']} EUR`\n"
            f"• *Time*: `{transaction['timestamp']}`\n"
            f"• *Error*: `{transaction.get('error', 'Unknown error')}`"
        )
    
    return message

def format_config_notification(config):
    """
    Format a configuration notification message.
    
    Args:
        config: The application configuration
        
    Returns:
        str: Formatted message
    """
    message = (
        f"🚀 *Coinbase Scheduler Started*\n\n"
        f"• *Product*: `{config.PRODUCT_ID}`\n"
        f"• *Amount*: `{config.AMOUNT} EUR`\n"
    )
    
    if config.ORDER_FREQUENCY == 'daily':
        message += f"• *Schedule*: `Daily at {config.BUY_TIME} UTC`\n"
    elif config.ORDER_FREQUENCY == 'weekly':
        message += f"• *Schedule*: `Weekly on {config.WEEKLY_DAY.capitalize()} at {config.BUY_TIME} UTC`\n"
    else:  # monthly
        message += f"• *Schedule*: `Monthly on day {config.MONTHLY_DAY} at {config.BUY_TIME} UTC`\n"
    
    return message

def send_startup_notification(config):
    """
    Send a notification with the current configuration when the application starts.
    
    Args:
        config: The application configuration
        
    Returns:
        None
    """
    if not TELEGRAM_NOTIFICATIONS_ENABLED:
        return
        
    # Format the notification message
    message = format_config_notification(config)
    
    # Send the notification
    send_telegram_notification(message)

def format_order_filled_notification(order_details, original_transaction):
    """
    Format an order filled notification message.
    
    Args:
        order_details (dict): Order details from get_order API
        original_transaction (dict): Original transaction details
        
    Returns:
        str: Formatted message
    """
    # Handle nested structure if present
    if 'order' in order_details:
        order_data = order_details['order']
    else:
        order_data = order_details
        
    # Extract relevant information from order details
    status = order_data.get('status', 'unknown')
    filled_value = order_data.get('filled_value', '0')
    filled_size = order_data.get('filled_size', '0')
    total_fees = order_data.get('total_fees', '0')
    average_filled_price = order_data.get('average_filled_price', '0')
    
    message = (
        f"✅ *Coinbase Order Filled*\n\n"
        f"• *Product*: `{original_transaction['product_id']}`\n"
        f"• *Order ID*: `{original_transaction['order_id']}`\n"
        f"• *Status*: `{status}`\n"
        f"• *Filled Value*: `{filled_value} EUR`\n"
        f"• *Filled Size*: `{filled_size}`\n"
        f"• *Average Price*: `{average_filled_price}`\n"
        f"• *Total Fees*: `{total_fees} EUR`\n"
        f"• *Time*: `{order_data.get('last_fill_time') or order_data.get('created_time', original_transaction['timestamp'])}`"
    )
    
    return message

def send_order_notification(transaction):
    """
    Send a notification for an order transaction.
    
    Args:
        transaction (dict): Transaction details
        
    Returns:
        None
    """
    if not TELEGRAM_NOTIFICATIONS_ENABLED:
        return
        
    # Format the notification message
    message = format_order_notification(transaction)
    
    # Send the notification
    send_telegram_notification(message)

def send_order_filled_notification(order_details, original_transaction):
    """
    Send a notification when an order is filled.
    
    Args:
        order_details (dict): Order details from get_order API
        original_transaction (dict): Original transaction details
        
    Returns:
        None
    """
    if not TELEGRAM_NOTIFICATIONS_ENABLED:
        return
        
    # Format the notification message
    message = format_order_filled_notification(order_details, original_transaction)
    
    # Send the notification
    send_telegram_notification(message)


