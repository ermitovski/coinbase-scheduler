import logging
from datetime import datetime
from decimal import Decimal
from coinbase_advanced_trader.enhanced_rest_client import EnhancedRESTClient
from app import config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('coinbase_app')

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
    """Execute the daily BTC-EUR buy order"""
    try:
        client = get_client()
        
        # Get current BTC-EUR price information
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
        error_msg = f"Failed to execute daily buy: {str(e)}"
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

def get_account_balance():
    """Get current balance for the specified cryptocurrency"""
    try:
        client = get_client()
        base_currency = config.PRODUCT_ID.split('-')[0]
        
        try:
            balance = client.get_crypto_balance(base_currency)
            # Convert to float if it's a string or Decimal
            if not isinstance(balance, (int, float)):
                balance = float(balance)
                
            return {
                'currency': base_currency,
                'balance': balance
            }
        except Exception as e:
            logger.error(f"Error getting balance via get_crypto_balance: {str(e)}")
            
            # Fallback: try to get account information directly
            try:
                accounts = client.list_accounts()
                
                # Handle different response types
                if hasattr(accounts, 'accounts'):
                    # Object with accounts attribute
                    for account in accounts.accounts:
                        if account.currency == base_currency:
                            available_balance = float(account.available_balance.value)
                            return {
                                'currency': base_currency,
                                'balance': available_balance
                            }
                elif isinstance(accounts, dict) and 'accounts' in accounts:
                    # Dictionary with accounts key
                    for account in accounts['accounts']:
                        if account.get('currency') == base_currency:
                            available_balance = float(account.get('available_balance', {}).get('value', 0))
                            return {
                                'currency': base_currency,
                                'balance': available_balance
                            }
                
                logger.warning(f"Could not find account for {base_currency}")
                return {
                    'currency': base_currency,
                    'balance': 0.0
                }
            except Exception as inner_e:
                logger.error(f"Fallback balance retrieval failed: {str(inner_e)}")
                raise
    except Exception as e:
        logger.error(f"Failed to get account balance: {str(e)}")
        return {
            'currency': base_currency if 'base_currency' in locals() else 'Unknown',
            'balance': 0.0,
            'error': str(e)
        }

def get_transaction_history():
    """Return the transaction history"""
    return transaction_history
