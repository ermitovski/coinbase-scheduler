## [v1.0.3] - 2025-05-28



### 🚀 Features
- feat: use GitHub usernames in changelog contributors ([37a772a](https://github.com/ermitovski/coinbase-scheduler/commit/37a772a12c72745d4e3ac71e9688fdfcc03fb308))
- feat: add automatic changelog generation on releases ([fd305f5](https://github.com/ermitovski/coinbase-scheduler/commit/fd305f520779a77c39871ab4703bc6d4f45644de))
### 🐛 Bug Fixes
- fix: resolve PR creation permission issues in release workflows ([6e4ce77](https://github.com/ermitovski/coinbase-scheduler/commit/6e4ce7727d3d4abce1cf40f32713945172f457c5))
- fix: add base branch for PR creation in release workflows ([a7e27b8](https://github.com/ermitovski/coinbase-scheduler/commit/a7e27b81ce8623a9b3c80bb176b609f43578c6c9))
- fix: prevent duplicate contributors in changelog ([a435ccb](https://github.com/ermitovski/coinbase-scheduler/commit/a435ccb839304e9ab29ac5c77c43c5fa7e6b0d66))
- fix: disable debug logging by default ([452ab5f](https://github.com/ermitovski/coinbase-scheduler/commit/452ab5fc2c7a8d9b67db09830713bf288a47325f))
- fixed order status but needs review ([bcf6589](https://github.com/ermitovski/coinbase-scheduler/commit/bcf6589680ed341f3f4cefdfa3f2d0404733bddb))
- fix image docker-compose ([9ca5a5c](https://github.com/ermitovski/coinbase-scheduler/commit/9ca5a5ceea15ab8483595c30ff7b73f70de4381b))
### 🔧 Maintenance & Other Changes

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

