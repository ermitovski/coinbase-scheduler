import logging
from datetime import datetime
from coinbase_advanced_trader.enhanced_rest_client import EnhancedRESTClient
from coinbase_scheduler import config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('coinbase_scheduler.trading')

# Transaction history
transaction_history = []

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

def execute_daily_buy():
    """Execute the daily crypto buy order"""
    try:
        client = get_client()
        
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
            fiat_amount=str(config.DAILY_AMOUNT)
        )
        
        # Log the transaction
        transaction = {
            'timestamp': datetime.utcnow().isoformat(),
            'product_id': config.PRODUCT_ID,
            'amount': config.DAILY_AMOUNT,
            'price': current_price,
            'order_id': order_result.id if hasattr(order_result, 'id') else str(order_result.get('id', "Unknown")),
            'status': 'Success'
        }
        transaction_history.append(transaction)
        
        logger.info(f"Successfully placed buy order for {config.DAILY_AMOUNT} EUR of {config.PRODUCT_ID}")
        return transaction
    except Exception as e:
        error_msg = f"Failed to execute buy: {str(e)}"
        logger.error(error_msg)
        
        # Log the failure
        transaction = {
            'timestamp': datetime.utcnow().isoformat(),
            'product_id': config.PRODUCT_ID,
            'amount': config.DAILY_AMOUNT,
            'price': None,
            'order_id': None,
            'status': 'Failed',
            'error': str(e)
        }
        transaction_history.append(transaction)
        
        return transaction

def get_transaction_history():
    """Return the transaction history"""
    return transaction_history
