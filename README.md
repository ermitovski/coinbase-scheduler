# Coinbase Automated Trader

A Docker-based application with a web interface for automated daily purchases of cryptocurrencies on Coinbase.

## Features

- Automated daily purchases of BTC-EUR (configurable)
- Web interface to monitor transactions and account balance
- Manual purchase capability
- Secure storage of API credentials
- Dockerized for easy deployment

## Setup

### Prerequisites

- Docker and Docker Compose
- Coinbase account with API access
- API key and secret with trading permissions

### Installation

1. Clone this repository:
   ```
   git clone <repository-url> /Users/xesteve/git/coinbase-app
   cd /Users/xesteve/git/coinbase-app
   ```

2. Create a `.env` file from the example:
   ```
   cp .env.example .env
   ```

3. Edit the `.env` file with your Coinbase API credentials and preferences:
   ```
   # Coinbase API credentials
   COINBASE_API_KEY=your-api-key
   COINBASE_API_SECRET=your-api-secret
   
   # Trading settings
   PRODUCT_ID=BTC-EUR
   DAILY_AMOUNT=30
   BUY_TIME=08:00
   
   # Flask settings
   FLASK_SECRET_KEY=your-secret-key
   FLASK_DEBUG=False
   
   # Admin credentials
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=your-secure-password
   ```

4. Build and start the Docker container:
   ```
   docker-compose up -d
   ```

5. Access the web interface at http://localhost:5000

## Usage

1. Log in to the dashboard using your admin credentials
2. View your current balance and transaction history
3. Modify settings if needed
4. Use the "Execute Buy Now" button to manually trigger a purchase

## Security

- API credentials are stored only in the `.env` file and are not exposed in the web interface
- All sensitive operations require authentication
- The application runs in a Docker container for isolation

## Development

To run the application in development mode:

```
docker-compose up
```

## License

MIT
