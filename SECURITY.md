# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| latest  | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability within this project, please follow these steps:

1. **Do NOT** disclose the vulnerability publicly until it has been addressed.
2. Email the details to the repository maintainer through GitHub.
3. Include the following in your report:
   - Description of the vulnerability
   - Steps to reproduce the issue
   - Potential impact
   - Suggested fix (if any)

### What to expect

- You will receive an acknowledgment within 48 hours.
- We will investigate and validate the issue within 7 days.
- We will release a patch as soon as possible, depending on complexity.
- We will publicly acknowledge your responsible disclosure (unless you prefer to remain anonymous).

## Security Best Practices for Users

When using this application:

1. **Never commit `.env` files** or any files containing API keys to version control
2. **Use strong, unique API keys** for Coinbase and Telegram
3. **Regularly rotate your API keys**
4. **Limit API key permissions** to only what's necessary (trade permissions for Coinbase)
5. **Run the application in a secure environment**
6. **Keep dependencies up to date** by regularly updating the Docker image

## Security Features

This application implements several security measures:

- All sensitive data (API keys, tokens) are stored in environment variables
- No hardcoded credentials in the source code
- Docker containers run with minimal privileges
- Dependencies are regularly updated
- Secure communication with external APIs (HTTPS only)

## Compliance

This application is designed to work with financial APIs. Users are responsible for:
- Complying with their local financial regulations
- Securing their own API credentials
- Monitoring their automated trading activities