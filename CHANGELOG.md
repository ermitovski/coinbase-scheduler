# Changelog

All notable changes to this project will be documented in this file.

## [v1.0.4] - 2025-05-30

## What's Changed

### 🚀 Features
- feat: add manual buy operations and configuration display [`5902e26`](https://github.com/ermitovski/coinbase-scheduler/commit/5902e26)

### 🐛 Bug Fixes
- fix: update system packages in Docker image to resolve security vulnerabilities [`f5697d0`](https://github.com/ermitovski/coinbase-scheduler/commit/f5697d0)

### 📚 Documentation
- docs: update CHANGELOG.md for v1.0.3 [`22716e9`](https://github.com/ermitovski/coinbase-scheduler/commit/22716e9)

### 📝 Other Changes
- Merge pull request #13 from ermitovski/changelog-update-v1.0.3 [`841ee06`](https://github.com/ermitovski/coinbase-scheduler/commit/841ee06)


## 🐳 Docker Images

Pull the latest image:
```bash
docker pull ghcr.io/ermitovski/coinbase-scheduler:v1.0.4
docker pull ghcr.io/ermitovski/coinbase-scheduler:latest
```

Run with Docker Compose:
```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# Development deployment
docker-compose up -d
```

## 🚀 Quick Start

```bash
# Create your .env file
cp .env.example .env

# Edit your configuration
nano .env

# Run the scheduler
docker run -d \
  --name coinbase-scheduler \
  --env-file .env \
  ghcr.io/ermitovski/coinbase-scheduler:v1.0.4
```

## 👥 Contributors

- @ermitovski
- Xavi Esteve

**Full Changelog**: https://github.com/ermitovski/coinbase-scheduler/compare/v1.0.3...v1.0.4

---

## [v1.0.3] - 2025-05-28

## What's Changed

### 🚀 Features
- feat: add automatic changelog generation on releases [`fd305f5`](https://github.com/ermitovski/coinbase-scheduler/commit/fd305f5)
- feat: use GitHub usernames in changelog contributors [`37a772a`](https://github.com/ermitovski/coinbase-scheduler/commit/37a772a)

### 🐛 Bug Fixes
- fix: disable debug logging by default [`452ab5f`](https://github.com/ermitovski/coinbase-scheduler/commit/452ab5f)
- fix: prevent duplicate contributors in changelog [`a435ccb`](https://github.com/ermitovski/coinbase-scheduler/commit/a435ccb)
- fix: add base branch for PR creation in release workflows [`a7e27b8`](https://github.com/ermitovski/coinbase-scheduler/commit/a7e27b8)
- fix: resolve PR creation permission issues in release workflows [`6e4ce77`](https://github.com/ermitovski/coinbase-scheduler/commit/6e4ce77)
- fix: clean up temporary files before creating changelog PR [`3d58307`](https://github.com/ermitovski/coinbase-scheduler/commit/3d58307)
- fix: prevent duplicate workflow runs on release [`183496c`](https://github.com/ermitovski/coinbase-scheduler/commit/183496c)

### 🔧 Maintenance
- chore: remove Update Release Notes workflow [`c291a60`](https://github.com/ermitovski/coinbase-scheduler/commit/c291a60)
- refactor: consolidate release workflows into single file [`7cb3579`](https://github.com/ermitovski/coinbase-scheduler/commit/7cb3579)

### 📝 Other Changes
- Only apply 'latest' tag to release builds [`237b0c6`](https://github.com/ermitovski/coinbase-scheduler/commit/237b0c6)
- Update documentation with latest features and badges [`56eb3a6`](https://github.com/ermitovski/coinbase-scheduler/commit/56eb3a6)
- Remove Docker Hub pulls badge [`1a01bb0`](https://github.com/ermitovski/coinbase-scheduler/commit/1a01bb0)
- fix image docker-compose [`9ca5a5c`](https://github.com/ermitovski/coinbase-scheduler/commit/9ca5a5c)
- monitor filled orders [`4e9bbe6`](https://github.com/ermitovski/coinbase-scheduler/commit/4e9bbe6)
- fixed order status but needs review [`bcf6589`](https://github.com/ermitovski/coinbase-scheduler/commit/bcf6589)


## 🐳 Docker Images

Pull the latest image:
```bash
docker pull ghcr.io/ermitovski/coinbase-scheduler:v1.0.3
docker pull ghcr.io/ermitovski/coinbase-scheduler:latest
```

Run with Docker Compose:
```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# Development deployment
docker-compose up -d
```

## 🚀 Quick Start

```bash
# Create your .env file
cp .env.example .env

# Edit your configuration
nano .env

# Run the scheduler
docker run -d \
  --name coinbase-scheduler \
  --env-file .env \
  ghcr.io/ermitovski/coinbase-scheduler:v1.0.3
```

## 👥 Contributors

- @ermitovski
- Xavi Esteve

**Full Changelog**: https://github.com/ermitovski/coinbase-scheduler/compare/v1.0.2...v1.0.3

---

