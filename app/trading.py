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

# ----- New functions for Coinbase API transactions -----

def get_coinbase_transactions(page=1, limit=10):
    """
    Fetch transactions directly from Coinbase API
    
    Args:
        page: Page number (1-based)
        limit: Number of records per page
    
    Returns:
        tuple: (transactions, has_more) where transactions is a list of transaction objects
               and has_more is a boolean indicating if there are more pages
    """
    try:
        client = get_client()
        transactions = []
        has_more = False
        
        # Calculate offset based on page number
        offset = (page - 1) * limit
        
        # Since we know the client has list_orders method, we'll use that directly
        if hasattr(client, 'list_orders'):
            try:
                # Use list_orders method to get transactions
                orders_response = client.list_orders(limit=limit, offset=offset)
                
                # Extract orders from the response
                orders = []
                if hasattr(orders_response, 'orders'):
                    orders = orders_response.orders
                elif isinstance(orders_response, dict) and 'orders' in orders_response:
                    orders = orders_response['orders']
                elif isinstance(orders_response, list):
                    orders = orders_response
                
                if orders:
                    # Standardize the orders for display
                    transactions = standardize_transactions(orders, 'order')
                    
                    # Assume there's more if we got a full page
                    has_more = len(orders) >= limit
                    logger.info(f"Retrieved {len(transactions)} orders from Coinbase API")
                else:
                    logger.warning("No orders found in the response")
            except Exception as list_orders_error:
                logger.error(f"Error using list_orders: {str(list_orders_error)}")
                # Fallback to in-memory transactions
                return (transaction_history, False)
        else:
            logger.warning("Client does not have list_orders method")
            # Fallback to in-memory transactions
            return (transaction_history, False)
        
        return (transactions, has_more)
        
    except Exception as e:
        logger.error(f"Failed to get Coinbase transactions: {str(e)}")
        return ([], False)

# These functions are no longer needed as we're using the more direct approach
# def get_orders_from_api
# def get_fills_from_api
# def extract_orders
# def extract_fills

def parse_api_string(data_string):
    """
    Parse a string that represents a Python dictionary or object.
    This is needed because some API responses come as stringified Python objects.
    
    Args:
        data_string: The string to parse
        
    Returns:
        Dict: The parsed data as a dictionary
    """
    if not isinstance(data_string, str):
        return data_string
        
    try:
        # Try to use ast.literal_eval which is safer than eval
        import ast
        return ast.literal_eval(data_string)
    except (SyntaxError, ValueError) as e:
        logger.error(f"Error parsing string with ast.literal_eval: {str(e)}")
        
        # Fallback: Try to manually parse the string
        # This is a simplified approach for common patterns
        if data_string.startswith('{') and data_string.endswith('}'):
            result = {}
            try:
                # Replace Python-style quotes with double quotes for JSON
                json_string = data_string.replace("'", '"')
                import json
                return json.loads(json_string)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse as JSON: {data_string[:100]}...")
        
        # Return the original string if all parsing attempts fail
        return {"raw_string": data_string}

def standardize_transactions(transactions, tx_type='order'):
    """Convert various transaction formats to a standard format"""
    standardized = []
    
    for tx in transactions:
        # Handle string representations
        if isinstance(tx, str):
            tx = parse_api_string(tx)
            
        # Convert to dictionary if it's an object
        if not isinstance(tx, dict) and hasattr(tx, '__dict__'):
            # Convert the object to a dictionary for raw_data
            raw_data = {}
            for attr in dir(tx):
                if not attr.startswith('_') and not callable(getattr(tx, attr)):
                    try:
                        value = getattr(tx, attr)
                        # Try to convert complex objects to strings
                        if not isinstance(value, (str, int, float, bool, type(None), list, dict)):
                            value = str(value)
                        raw_data[attr] = value
                    except Exception as e:
                        raw_data[attr] = f"Error: {str(e)}"
            
            # Also convert tx to a dictionary for attribute access
            tx = {k: v for k, v in raw_data.items()}
        elif isinstance(tx, dict):
            # Make a copy of the dictionary for raw_data to avoid reference issues
            raw_data = tx.copy()
            
            # Make sure all values in raw_data are JSON serializable
            for key, value in raw_data.items():
                if isinstance(value, str) and (value.startswith('{') or value.startswith("'")):
                    # Try to parse string representation of dictionaries
                    try:
                        parsed_value = parse_api_string(value)
                        if isinstance(parsed_value, dict):
                            raw_data[key] = parsed_value
                    except Exception as e:
                        logger.warning(f"Error parsing string value for key {key}: {str(e)}")
                elif not isinstance(value, (str, int, float, bool, type(None), list, dict)):
                    raw_data[key] = str(value)
        else:
            # If it's neither a dict nor an object with __dict__, convert to string
            raw_data = {"data": str(tx)}
        
        # Create a standardized transaction object
        std_tx = {
            'order_id': get_attr(tx, ['id', 'order_id']),
            'product_id': get_attr(tx, ['product_id']),
            'side': get_attr(tx, ['side']),
            'order_type': get_attr(tx, ['type', 'order_type']),
            'size': get_attr(tx, ['size', 'base_size', 'filled_size']),
            'price': get_attr(tx, ['price', 'limit_price', 'average_filled_price']),
            'status': get_attr(tx, ['status', 'order_status']),
            'created_time': get_attr(tx, ['created_at', 'created_time']),
            'client_order_id': get_attr(tx, ['client_order_id']),
            'fee': get_attr(tx, ['fee', 'total_fees']),
            'settled': get_attr(tx, ['settled']),
            'raw_data': raw_data  # Use our JSON-serializable raw_data
        }
        
        standardized.append(std_tx)
    
    return standardized

def get_attr(obj, keys):
    """Safely get an attribute from an object or dictionary using a list of possible keys"""
    if isinstance(obj, dict):
        for key in keys:
            if key in obj and obj[key] is not None:
                return obj[key]
    else:
        for key in keys:
            if hasattr(obj, key) and getattr(obj, key) is not None:
                return getattr(obj, key)
    
    return None  # Return None if no key is found

def get_transaction_by_id(order_id):
    """Get a specific transaction by ID from Coinbase API"""
    try:
        client = get_client()
        
        # Now that we know get_order works, we'll focus on that method
        if hasattr(client, 'get_order'):
            try:
                order = client.get_order(order_id)
                logger.info(f"Got order using get_order method: {type(order)}")
                
                # Handle the GetOrderResponse object
                if hasattr(order, '__dict__'):
                    # It's an object with attributes
                    order_dict = {}
                    for attr in dir(order):
                        if not attr.startswith('_') and not callable(getattr(order, attr)):
                            try:
                                value = getattr(order, attr)
                                order_dict[attr] = value
                            except Exception as e:
                                logger.warning(f"Error getting attribute {attr}: {str(e)}")
                    
                    # If we have an 'order' attribute, use that
                    if hasattr(order, 'order') and getattr(order, 'order') is not None:
                        nested_order = getattr(order, 'order')
                        if isinstance(nested_order, dict):
                            order_dict = nested_order
                        elif hasattr(nested_order, '__dict__'):
                            order_dict = {k: getattr(nested_order, k) for k in dir(nested_order) 
                                        if not k.startswith('_') and not callable(getattr(nested_order, k))}
                    
                    return standardize_transactions([order_dict], 'order')[0]
                elif isinstance(order, dict):
                    # It's already a dictionary
                    return standardize_transactions([order], 'order')[0]
                else:
                    # Convert to string as fallback
                    logger.warning(f"Unexpected order type: {type(order)}")
                    order_dict = {'id': order_id, 'data': str(order)}
                    return standardize_transactions([order_dict], 'order')[0]
                
            except Exception as order_error:
                # If get_order fails, check in-memory transactions as fallback
                logger.error(f"Error fetching order {order_id}: {str(order_error)}")
                
                # Check in-memory transactions
                for tx in transaction_history:
                    if tx.get('order_id') == order_id:
                        # Convert in-memory transaction to standard format
                        return {
                            'order_id': tx.get('order_id'),
                            'product_id': tx.get('product_id'),
                            'side': 'BUY',  # Assuming all in-memory transactions are buys
                            'order_type': 'LIMIT',
                            'size': None,  # We don't track size in in-memory transactions
                            'price': tx.get('price'),
                            'status': 'Success' if tx.get('status') == 'Success' else 'Failed',
                            'created_time': tx.get('timestamp'),
                            'client_order_id': None,
                            'fee': None,
                            'settled': True,
                            'raw_data': tx  # In-memory transactions are already JSON serializable
                        }
                
                # If we get here, order wasn't found
                return None
        else:
            logger.warning("Client does not have get_order method")
            return None
        
    except Exception as e:
        logger.error(f"Failed to get transaction by ID: {str(e)}")
        return None
