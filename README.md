# Coinbase Scheduler

A simplified scheduler tool to execute recurring cryptocurrency purchases on Coinbase. This tool automates the process of buying a specified amount of cryptocurrency at regular intervals (daily, weekly, or monthly).

## Features

- Automated cryptocurrency purchasing on a daily, weekly, or monthly schedule
- Configurable purchase amount and timing
- Support for any Coinbase-supported cryptocurrency pair
- Command-line interface for manual operations
- Docker support for easy deployment

## Setup

### Prerequisites

- Python 3.9+
- Coinbase Advanced Trade API keys

### Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Copy the example environment file and configure it:
   ```
   cp .env.example .env
   ```
4. Edit the `.env` file with your Coinbase API credentials and preferred purchase settings

## Configuration

The application is configured through environment variables, which can be set in the `.env` file:

- `COINBASE_API_KEY`: Your Coinbase Advanced Trade API key
- `COINBASE_API_SECRET`: Your Coinbase Advanced Trade API secret
- `PRODUCT_ID`: The cryptocurrency pair to trade (e.g., `BTC-EUR`)
- `AMOUNT`: The amount of fiat currency to use for each purchase
- `BUY_TIME`: The time to execute purchases (in UTC, format: HH:MM)
- `ORDER_FREQUENCY`: Frequency of purchases (`daily`, `weekly`, or `monthly`)
- `WEEKLY_DAY`: Day of the week for weekly purchases (`monday`, `tuesday`, etc.)
- `MONTHLY_DAY`: Day of the month (1-28) for monthly purchases

## Usage

### Running the Scheduler

To start the scheduler and keep it running in the background:

```
python coinbase_scheduler.py
```

### Manual Operations

Execute a one-time purchase:

```
python coinbase_scheduler.py --buy-now
```

Show current configuration:

```
python coinbase_scheduler.py --show-config
```

## Docker Deployment

Build and run using Docker Compose:

```
docker-compose up -d
```

This will start the scheduler in a Docker container.

## Logging

Logs are output to the console, and can be redirected to a file if needed:

```
python coinbase_scheduler.py > coinbase_scheduler.log 2>&1
```

## License

MIT
