import logging
from datetime import datetime, timezone
from coinbase_advanced_trader.enhanced_rest_client import EnhancedRESTClient
from coinbase_scheduler import config
from coinbase_scheduler.notifications import send_order_notification, send_order_filled_notification

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('coinbase_scheduler.trading')
logger.setLevel(logging.INFO)

# Transaction history
transaction_history = []

# Pending orders to monitor
pending_orders = {}

def get_client():
    """Initialize and return a Coinbase client"""
    try:
        client = EnhancedRESTClient(
            api_key=config.COINBASE_API_KEY,
            api_secret=config.COINBASE_API_SECRET
        )
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Coinbase client: {str(e)}")
        raise

def execute_buy(amount=None):
    """
    Execute the crypto buy order
    
    Args:
        amount (float, optional): Custom amount to use for this buy. Defaults to None.
        
    Returns:
        dict: Result of the buy operation
    """
    try:
        client = get_client()
        
        # Use the provided amount or fall back to the configured amount
        buy_amount = amount if amount is not None else config.AMOUNT
        
        # Get current price information
        product_info = client.get_product(product_id=config.PRODUCT_ID)
        
        # Handle different response types from the API
        if hasattr(product_info, 'price'):
            # It's an object with attributes
            current_price = product_info.price
        elif isinstance(product_info, dict) and 'price' in product_info:
            # It's a dictionary
            current_price = product_info['price']
        else:
            # Log structure for debugging
            logger.error(f"Unexpected product_info structure: {type(product_info)}: {product_info}")
            raise ValueError("Could not determine current price from API response")
        
        logger.info(f"Current price for {config.PRODUCT_ID}: {current_price}")
        
        # Place a limit buy order
        order_result = client.fiat_limit_buy(
            product_id=config.PRODUCT_ID,
            fiat_amount=str(buy_amount)
        )
        
        # Log the transaction
        transaction = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'product_id': config.PRODUCT_ID,
            'amount': buy_amount,
            'price': current_price,
            'order_id': order_result.id if hasattr(order_result, 'id') else str(order_result.get('id', "Unknown")),
            'status': 'Success'
        }
        transaction_history.append(transaction)
        
        # Send notification
        send_order_notification(transaction)
        
        # Add to pending orders if we have a valid order ID
        if transaction['order_id'] and transaction['order_id'] != "Unknown":
            pending_orders[transaction['order_id']] = {
                'transaction': transaction,
                'created_at': datetime.now(timezone.utc),
                'last_checked': datetime.now(timezone.utc)
            }
            logger.info(f"Added order {transaction['order_id']} to pending orders monitoring")
        
        logger.info(f"Successfully placed buy order for {buy_amount} EUR of {config.PRODUCT_ID}")
        return transaction
    except Exception as e:
        error_msg = f"Failed to execute buy: {str(e)}"
        logger.error(error_msg)
        
        # Use the provided amount or fall back to the configured amount
        buy_amount = amount if amount is not None else config.AMOUNT
        
        # Log the failure
        transaction = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'product_id': config.PRODUCT_ID,
            'amount': buy_amount,
            'price': None,
            'order_id': None,
            'status': 'Failed',
            'error': str(e)
        }
        transaction_history.append(transaction)
        
        # Send notification for failed order
        send_order_notification(transaction)
        
        return transaction

def check_order_status(order_id):
    """
    Check the status of an order by order ID
    
    Args:
        order_id (str): The order ID to check
        
    Returns:
        dict: Order status information
    """
    try:
        client = get_client()
        order = client.get_order(order_id)
        
        # Handle different response types
        if hasattr(order, '__dict__'):
            # Convert object to dict if needed
            order_dict = order.__dict__
        else:
            order_dict = order
            
        # Log the order structure for debugging
        logger.debug(f"Order {order_id} raw response type: {type(order)}")
        logger.debug(f"Order {order_id} data: {order_dict}")
        
        return order_dict
    except Exception as e:
        logger.error(f"Failed to check order status for {order_id}: {str(e)}")
        return None

def check_pending_orders():
    """
    Check the status of all pending orders and send notifications for filled orders.
    Orders are monitored until they are filled, cancelled, or failed.
    
    Returns:
        int: Number of orders checked
    """
    if not pending_orders:
        return 0
        
    orders_to_remove = []
    checked_count = 0
    current_time = datetime.now(timezone.utc)
    
    logger.info(f"Checking {len(pending_orders)} pending orders...")
    
    for order_id, order_info in pending_orders.items():
        try:
            # Check order status
            order_status = check_order_status(order_id)
            if order_status:
                checked_count += 1
                order_info['last_checked'] = current_time
                
                # Extract order data from nested structure
                if isinstance(order_status, dict) and 'order' in order_status:
                    order_data = order_status['order']
                elif hasattr(order_status, 'order'):
                    # It's an object with an order attribute
                    order_data = order_status.order
                else:
                    order_data = order_status
                
                # Convert to dict if it's not already
                if not isinstance(order_data, dict):
                    # Try to convert using the SDK's to_dict method if available
                    if hasattr(order_data, 'to_dict'):
                        order_data = order_data.to_dict()
                    elif hasattr(order_data, '__dict__'):
                        order_data = order_data.__dict__
                    else:
                        # Last resort: try to access attributes directly
                        try:
                            order_dict = {
                                'status': getattr(order_data, 'status', ''),
                                'completion_percentage': getattr(order_data, 'completion_percentage', '0'),
                                'filled_size': getattr(order_data, 'filled_size', '0'),
                                'filled_value': getattr(order_data, 'filled_value', '0'),
                                'total_fees': getattr(order_data, 'total_fees', '0'),
                                'average_filled_price': getattr(order_data, 'average_filled_price', '0'),
                                'last_fill_time': getattr(order_data, 'last_fill_time', None),
                                'created_time': getattr(order_data, 'created_time', ''),
                                'cancel_message': getattr(order_data, 'cancel_message', ''),
                            }
                            order_data = order_dict
                        except Exception as e:
                            logger.error(f"Failed to extract order attributes: {e}")
                            continue
                
                # Check if order is filled
                status = order_data.get('status', '').upper()
                logger.info(f"Order {order_id} status: {status}")
                
                # Also check completion percentage and filled size
                completion = order_data.get('completion_percentage', '0')
                filled_size = order_data.get('filled_size', '0')
                logger.debug(f"Order {order_id} completion: {completion}%, filled_size: {filled_size}")
                
                if status in ['FILLED', 'DONE', 'COMPLETED'] or completion == '100':
                    logger.info(f"Order {order_id} has been filled!")
                    send_order_filled_notification(order_data, order_info['transaction'])
                    orders_to_remove.append(order_id)
                elif status in ['CANCELLED', 'EXPIRED', 'FAILED', 'REJECTED']:
                    logger.info(f"Order {order_id} was {status}")
                    orders_to_remove.append(order_id)
                    # Send notification about order status
                    from coinbase_scheduler.notifications import send_telegram_notification
                    message = (
                        f"❌ *Order {status.capitalize()}*\n\n"
                        f"• *Product*: `{order_info['transaction']['product_id']}`\n"
                        f"• *Order ID*: `{order_id}`\n"
                        f"• *Amount*: `{order_info['transaction']['amount']} EUR`\n"
                        f"• *Status*: `{status}`\n"
                        f"• *Created*: `{order_info['created_at'].isoformat()}`"
                    )
                    send_telegram_notification(message)
                else:
                    # Order is still pending
                    age_hours = (current_time - order_info['created_at']).total_seconds() / 3600
                    logger.debug(f"Order {order_id} is still {status}, age: {age_hours:.1f} hours")
                    
        except Exception as e:
            logger.error(f"Error checking order {order_id}: {str(e)}")
            
    # Remove processed orders
    for order_id in orders_to_remove:
        del pending_orders[order_id]
        
    if checked_count > 0:
        logger.info(f"Checked {checked_count} orders, {len(orders_to_remove)} removed from monitoring")
        
    return checked_count

def get_pending_orders():
    """Return the pending orders"""
    return pending_orders

def get_transaction_history():
    """Return the transaction history"""
    return transaction_history
