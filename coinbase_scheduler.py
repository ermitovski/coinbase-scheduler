#!/usr/bin/env python3
import logging
import time
import signal
import sys
import argparse
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('coinbase_scheduler')

# Load environment variables
load_dotenv()

# Import scheduler components
from coinbase_scheduler.scheduler import scheduler, init_scheduler, manual_buy, get_next_check_time
from coinbase_scheduler import config
from coinbase_scheduler.notifications import send_startup_notification

# Signal handler for graceful shutdown
def handle_shutdown(signum, frame):
    logger.info("Received shutdown signal, shutting down scheduler...")
    if scheduler.running:
        scheduler.shutdown()
    sys.exit(0)

def run_scheduler():
    """Start and run the scheduler process"""
    try:
        # Set up signal handlers
        signal.signal(signal.SIGINT, handle_shutdown)
        signal.signal(signal.SIGTERM, handle_shutdown)
        
        logger.info("Starting scheduler process...")
        
        # Validate configuration
        config.validate_config()
        
        # Initialize and start scheduler
        init_scheduler()
        
        logger.info("Scheduler started successfully")
        logger.info(f"Product: {config.PRODUCT_ID}")
        logger.info(f"Amount: {config.AMOUNT}")
        
        if config.ORDER_FREQUENCY == 'daily':
            logger.info(f"Schedule: Daily at {config.BUY_TIME} UTC")
        elif config.ORDER_FREQUENCY == 'weekly':
            logger.info(f"Schedule: Weekly on {config.WEEKLY_DAY.capitalize()} at {config.BUY_TIME} UTC")
        else:  # monthly
            logger.info(f"Schedule: Monthly on day {config.MONTHLY_DAY} at {config.BUY_TIME} UTC")
        
        # Send startup notification
        send_startup_notification(config)
        
        # Log next order check time
        next_check = get_next_check_time()
        if next_check:
            logger.info(f"Next order status check scheduled at: {next_check}")
        
        # Keep the process running until a signal is received
        while True:
            time.sleep(60)  # Sleep to reduce CPU usage
            
    except Exception as e:
        logger.error(f"Error in scheduler process: {str(e)}")
        sys.exit(1)

def execute_single_buy(amount=None):
    """Execute a single buy operation and exit"""
    try:
        logger.info("Executing manual buy operation...")
        
        # Validate configuration
        config.validate_config()
        
        # Log the amount being used
        if amount is not None:
            logger.info(f"Using custom amount: {amount} EUR (overriding configured amount: {config.AMOUNT} EUR)")
        else:
            logger.info(f"Using configured amount: {config.AMOUNT} EUR")
        
        # Execute the buy with optional custom amount
        result = manual_buy(amount=amount)
        
        logger.info(f"Buy operation completed: {result['status']}")
        if result['status'] == 'Success':
            logger.info(f"Order ID: {result['order_id']}")
            logger.info(f"Amount: {result['amount']} EUR")
            logger.info(f"Price: {result['price']}")
        else:
            logger.error(f"Error: {result.get('error', 'Unknown error')}")
            
        return 0 if result['status'] == 'Success' else 1
    except Exception as e:
        logger.error(f"Error executing buy: {str(e)}")
        return 1

def main():
    """Main entry point with command line arguments"""
    parser = argparse.ArgumentParser(description='Coinbase Scheduler')
    parser.add_argument('--buy-now', action='store_true', help='Execute a single buy operation and exit')
    parser.add_argument('--amount', type=float, help='Override the amount for a single buy operation (EUR)')
    parser.add_argument('--show-config', action='store_true', help='Display current configuration and exit')
    
    args = parser.parse_args()
    
    # Show configuration if requested
    if args.show_config:
        print("\nCoinbase Scheduler Configuration:")
        print(f"Product ID: {config.PRODUCT_ID}")
        print(f"Amount: {config.AMOUNT}")
        print(f"Buy Time: {config.BUY_TIME} UTC")
        print(f"Frequency: {config.ORDER_FREQUENCY}")
        if config.ORDER_FREQUENCY == 'weekly':
            print(f"Weekly Day: {config.WEEKLY_DAY.capitalize()}")
        elif config.ORDER_FREQUENCY == 'monthly':
            print(f"Monthly Day: {config.MONTHLY_DAY}")
        
        # Send configuration as Telegram notification
        send_startup_notification(config)
        
        return 0
        
    # Execute single buy if requested
    if args.buy_now:
        return execute_single_buy(amount=args.amount)
        
    # Otherwise, run the scheduler
    run_scheduler()
    return 0

if __name__ == "__main__":
    sys.exit(main())
