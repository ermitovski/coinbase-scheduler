# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Setup virtual environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the scheduler
```bash
python3 coinbase_scheduler.py
```

### Manual buy operations
```bash
# Execute a single buy with configured amount
python3 coinbase_scheduler.py --buy-now

# Execute a single buy with custom amount
python3 coinbase_scheduler.py --buy-now --amount 50
```

### Show configuration
```bash
python3 coinbase_scheduler.py --show-config
```

### Docker deployment
```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Development notes
- Always activate the virtual environment before running commands: `source venv/bin/activate`
- To deactivate the virtual environment: `deactivate`

## Architecture

This is a cryptocurrency purchase automation tool for Coinbase using the Advanced Trade API. The codebase follows a modular structure:

### Main Components

1. **coinbase_scheduler.py** - Entry point that handles CLI arguments and orchestrates the scheduler process
   - Signal handling for graceful shutdown
   - Command-line interface for manual operations and configuration display

2. **coinbase_scheduler/** - Core module package
   - **config.py** - Configuration management with environment variables and dynamic updates
   - **scheduler.py** - APScheduler-based scheduling logic for daily/weekly/monthly automated purchases
   - **trading.py** - Coinbase API integration using `coinbase-advancedtrade-python` library
   - **notifications.py** - Telegram bot integration for order notifications

### Key Design Patterns

- **Environment-based configuration**: All settings stored in `.env` file, with dynamic updates persisted via `python-dotenv`
- **Background scheduling**: Uses APScheduler with CronTrigger for reliable time-based execution
- **Error handling**: All trading operations include error capture and notification
- **Transaction history**: In-memory storage of transaction results (note: not persisted between restarts)

### API Integration

The application uses the `coinbase-advancedtrade-python` library's `EnhancedRESTClient` for:
- Product price queries via `get_product()`
- Fiat limit buy orders via `fiat_limit_buy()`

### Notification System

Telegram notifications are sent for:
- Scheduler startup with configuration details
- Successful buy orders with transaction details
- Failed orders with error information