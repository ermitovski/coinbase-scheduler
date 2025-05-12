import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
