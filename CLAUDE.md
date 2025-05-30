# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Local Development Environment Setup

#### Initial Setup
```bash
# Clone the repository
git clone https://github.com/ermitovski/coinbase-scheduler.git
cd coinbase-scheduler

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies (use python -m pip to avoid system pip issues)
python -m pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your configuration
```

#### Working with the Virtual Environment
```bash
# Always activate the virtual environment before working
source venv/bin/activate

# To deactivate when done
deactivate

# If you encounter pip issues on macOS, use the venv's Python directly:
./venv/bin/python -m pip install -r requirements.txt
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
# Development (builds locally)
docker-compose up -d

# Production (uses pre-built image from GitHub Container Registry)
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Development notes
- Always activate the virtual environment before running commands: `source venv/bin/activate`
- To deactivate the virtual environment: `deactivate`
- Run tests: Currently no automated tests (consider adding pytest)
- Lint/format: Consider adding ruff or black for Python formatting

## Conventional Commits

This project follows the [Conventional Commits](https://www.conventionalcommits.org/) specification for commit messages. This enables automatic changelog generation and better commit history.

### Commit Message Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code (white-space, formatting, etc)
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **perf**: A code change that improves performance
- **test**: Adding missing tests or correcting existing tests
- **build**: Changes that affect the build system or external dependencies
- **ci**: Changes to CI configuration files and scripts
- **chore**: Other changes that don't modify src or test files
- **revert**: Reverts a previous commit

### Examples

```bash
# Feature
git commit -m "feat: add weekly scheduling option"

# Bug fix
git commit -m "fix: resolve order status tracking issue"

# Documentation
git commit -m "docs: update README with new configuration options"

# Breaking change (note the ! after type)
git commit -m "feat!: change API authentication method"

# Commit with scope
git commit -m "feat(trading): implement market order support"

# Commit with body
git commit -m "fix: prevent duplicate orders

- Add transaction ID tracking
- Check for pending orders before placing new ones
- Log all order attempts"
```

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

## CI/CD Pipeline

### GitHub Actions Workflow

The repository uses GitHub Actions for automated builds and deployments:

1. **Triggers**:
   - Push to `main` branch
   - Pull requests to `main`
   - GitHub releases
   - Manual workflow dispatch

2. **Build Process**:
   - Builds multi-architecture Docker images (linux/amd64, linux/arm64)
   - Uses Docker buildx for cross-platform builds
   - Pushes to GitHub Container Registry (ghcr.io)

3. **Security Scanning**:
   - **Trivy vulnerability scanner**: Scans Docker images for OS and library vulnerabilities
   - **Trivy secret scanner**: Scans repository for exposed secrets
   - Results uploaded to GitHub Security tab
   - Fails on CRITICAL/HIGH vulnerabilities

4. **Image Tagging**:
   - `main` branch: `main`, `sha-<commit>`
   - Pull requests: `pr-<number>`
   - Releases: `v1.2.3`, `1.2`, `1`, `latest`, `sha-<commit>`
   - Note: `latest` tag only applied on releases

### Development Workflow

1. **Creating a new feature**:
   ```bash
   git checkout -b feature/your-feature-name
   # Make changes
   git add .
   git commit -m "Add your feature"
   git push -u origin feature/your-feature-name
   ```

2. **Pull Request Process**:
   - Create PR against `main` branch
   - CI will build and scan the Docker image
   - Wait for all checks to pass
   - Request review if needed

3. **Release Process**:
   - Merge PR to `main`
   - Create a new release on GitHub
   - Tag with semantic version (e.g., `v1.2.3`)
   - CI will automatically build, scan, and publish Docker images
   - Release notes are automatically generated with:
     - Changelog based on commit history
     - Docker pull commands
     - Quick start instructions
     - Contributors list

4. **Changelog Generation**:
   - Automatic changelog creation on releases
   - Parses conventional commits for better formatting
   - Groups changes by type (features, fixes, etc.)
   - Creates pull request to update CHANGELOG.md
   - Updates release description with formatted notes

### Dependency Management

- **Dependabot** is enabled for:
  - Python dependencies (pip)
  - GitHub Actions
  - Docker base images
- PRs are automatically created for dependency updates
- Review and merge dependency PRs regularly

### Security Best Practices

1. **Never commit secrets** - Use environment variables
2. **Review Trivy scan results** - Fix vulnerabilities before release
3. **Keep dependencies updated** - Merge Dependabot PRs promptly
4. **Use specific versions** - Avoid using `latest` tags in production

### Monitoring and Logs

- Check GitHub Actions tab for build status
- Review Security tab for vulnerability reports
- Docker logs available via `docker logs` or `docker-compose logs`
- Consider adding application metrics/monitoring for production