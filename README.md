# Coinbase Scheduler

[![Docker Build](https://github.com/ermitovski/coinbase-scheduler/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/ermitovski/coinbase-scheduler/actions/workflows/docker-publish.yml)
[![GitHub release](https://img.shields.io/github/release/ermitovski/coinbase-scheduler.svg)](https://github.com/ermitovski/coinbase-scheduler/releases)
[![Security](https://img.shields.io/badge/security-enabled-brightgreen)](https://github.com/ermitovski/coinbase-scheduler/security)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A simplified scheduler tool to execute recurring cryptocurrency purchases on Coinbase. This tool automates the process of buying a specified amount of cryptocurrency at regular intervals (daily, weekly, or monthly).

## Features

- 🤖 Automated cryptocurrency purchasing on a daily, weekly, or monthly schedule
- ⚙️ Configurable purchase amount and timing
- 💱 Support for any Coinbase-supported cryptocurrency pair
- 💬 Telegram notifications for order status
- 🖥️ Command-line interface for manual operations
- 🐳 Docker support with multi-architecture images (amd64/arm64)
- 🔒 Security scanning with Trivy for vulnerabilities and secrets
- 🔄 Automated dependency updates with Dependabot
- ⚡ GitHub Actions CI/CD pipeline

## Setup

### Prerequisites

- Python 3.9+
- Coinbase Advanced Trade API keys
- (Optional) Telegram Bot token for notifications
- (Optional) Docker for containerized deployment

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ermitovski/coinbase-scheduler.git
   cd coinbase-scheduler
   ```

2. Create and activate a Python virtual environment:
   ```bash
   # Create virtual environment
   python3 -m venv venv
   
   # Activate virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   # venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   # Using pip directly
   pip install -r requirements.txt
   
   # Or using python -m pip (recommended)
   python -m pip install -r requirements.txt
   ```

4. Copy the example environment file and configure it:
   ```bash
   cp .env.example .env
   ```

5. Edit the `.env` file with your Coinbase API credentials and preferred purchase settings

### Local Development Setup

For development, always work within the virtual environment:

```bash
# Activate the virtual environment
source venv/bin/activate

# When done, deactivate it
deactivate
```

If you encounter issues with pip on macOS, use the virtual environment's Python directly:
```bash
./venv/bin/python -m pip install -r requirements.txt
```

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
- `TELEGRAM_BOT_TOKEN`: (Optional) Telegram bot token for notifications
- `TELEGRAM_CHAT_ID`: (Optional) Telegram chat ID for notifications

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

### Using Pre-built Images

Pre-built multi-architecture images (amd64/arm64) are available on GitHub Container Registry:

```bash
# Pull the latest release
docker pull ghcr.io/ermitovski/coinbase-scheduler:latest

# Or pull a specific version
docker pull ghcr.io/ermitovski/coinbase-scheduler:v1.0.0
```

Run the container:

```bash
docker run -d \
  --name coinbase-scheduler \
  --env-file .env \
  --restart unless-stopped \
  ghcr.io/ermitovski/coinbase-scheduler:latest
```

### Using Docker Compose

For development:
```bash
docker-compose up -d
```

For production (uses pre-built image):
```bash
docker-compose -f docker-compose.prod.yml up -d
```

View logs:
```bash
docker-compose logs -f
```

## Security

- 🔐 All Docker images are automatically scanned for vulnerabilities using Trivy
- 🔍 Repository is scanned for secrets and sensitive information
- 📦 Dependencies are automatically updated via Dependabot
- 🛡️ See [SECURITY.md](SECURITY.md) for our security policy

## Contributing

We welcome contributions! Please follow these guidelines:

### Commit Messages

This project uses [Conventional Commits](https://www.conventionalcommits.org/) for clear and structured commit messages:

```bash
# Format: <type>(<scope>): <subject>

# Examples:
git commit -m "feat: add support for EUR trading pairs"
git commit -m "fix: resolve connection timeout issues"
git commit -m "docs: update configuration examples"
git commit -m "chore: update dependencies"
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`

### Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes following the commit conventions
4. Push to your fork: `git push origin feature/your-feature`
5. Create a Pull Request

### Releases

When a new release is created:
- Changelog is automatically generated from commit history
- Docker images are built and pushed to GitHub Container Registry
- Release notes include installation instructions and changes

## CI/CD

This project uses GitHub Actions for continuous integration and deployment:

- **On Push to main**: Builds and pushes Docker images with `main` tag
- **On Pull Request**: Builds images for testing (no push)
- **On Release**: 
  - Builds and pushes images with version tags and `latest`
  - Automatically generates changelog from commit history
  - Updates release notes with Docker commands and quick start guide
  - Creates pull request to update CHANGELOG.md

All builds include:
- Multi-architecture support (linux/amd64, linux/arm64)
- Vulnerability scanning with Trivy
- Secret scanning
- Automated release notes generation

## Logging

Logs are output to the console and include:
- Scheduler startup confirmation
- Scheduled job registrations
- Order execution results
- Error messages

When using Docker, view logs with:
```bash
docker logs -f coinbase-scheduler
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

[MIT](LICENSE) - see the LICENSE file for details.
