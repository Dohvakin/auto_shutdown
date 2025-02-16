# TrueNAS Automated Shutdown System

A Dockerized service that monitors power status and initiates graceful TrueNAS shutdowns via WebSocket API.

## Project Structure

Key files:
- `shutdown_script.py` - Main Python logic for power checks and shutdown procedures
- `entrypoint.sh` - Container entrypoint that configures cron scheduling
- `Dockerfile` - Builds the container image with Python 3.11 and required dependencies
- `docker-compose.yaml` - Docker configuration with environment variables
- `crontab` - Cron schedule configuration for regular checks
- `pyproject.toml` - Python dependencies specification
- `uv.lock` - Pinned dependency versions for reproducible builds
- `run_script.sh` - Helper script for manual execution and testing

## Features

- Real-time power monitoring via HTTP endpoint
- Configurable grace period with multiple verification checks
- Secure WebSocket communication with TrueNAS middleware
- Detailed logging with automatic log rotation (50MB limit)
- Timezone-aware timestamps (Asia/Kolkata by default)
- Docker-based deployment with cron scheduling
- Environment variable configuration
- Fail-safe error handling with multiple verification stages

## Requirements

- Docker 20.10+ with compose plugin
- TrueNAS Scale 22.12+ with WebSocket API enabled
- Network-accessible power monitoring endpoint (HTTP/HTTPS)
- Persistent storage volume for logs (configured in docker-compose.yaml)

## Installation & Configuration

1. Clone repository:
```bash
git clone https://github.com/Dohvakin/auto_shutdown
cd auto_shutdown
```

2. Configure environment variables in `docker-compose.yaml`:
```yaml
services:
  truenas-shutdown:
    environment:
      TRUENAS_HOST: "nas.example.com:443"      # TrueNAS host:port
      TRUENAS_USERNAME: "admin"                # API user with shutdown privileges
      TRUENAS_PASSWORD: "secure_password"      # API user password
      USE_SSL: "true"                          # HTTPS connection to TrueNAS
      POWER_CHECK_URL: "http://192.168.1.11"   # Power monitoring endpoint
      INTERVAL_CHECK_ENABLED: "true"           # Enable verification checks
      CHECK_INTERVAL: "60"                     # 60 seconds between checks
      TOTAL_CHECKS: "5"                        # Confirmations before shutdown
```

3. Build and deploy:
```bash
docker compose build --no-cache
docker compose up -d
```

## Environment Variables Reference

| Variable                | Required | Default     | Description                                                                 |
|-------------------------|----------|-------------|-----------------------------------------------------------------------------|
| TRUENAS_HOST            | Yes      | -           | TrueNAS host with port (e.g., 192.168.1.100:443)                            |
| TRUENAS_USERNAME        | Yes      | -           | TrueNAS API username with system privileges                                 |
| TRUENAS_PASSWORD        | Yes      | -           | TrueNAS API password                                                        |
| USE_SSL                 | No       | true        | Enable HTTPS for WebSocket connections (true/false)                         |
| INTERVAL_CHECK_ENABLED  | No       | false       | Enable multi-stage verification before shutdown (true/false)                |
| POWER_CHECK_URL         | Yes      | -           | HTTP endpoint for power status checks                                       |
| CHECK_INTERVAL          | No       | 60          | Seconds between checks when verification enabled (60-3600)                  |
| TOTAL_CHECKS            | No       | 5           | Consecutive failures required for shutdown (2-10)                           |

## Operational Modes

### Immediate Shutdown (INTERVAL_CHECK_ENABLED=false)
- Single power check
- Immediate shutdown if failure detected
- Recommended for stable power monitoring systems

### Verified Shutdown (INTERVAL_CHECK_ENABLED=true)
- Sequential power verification checks
- Configurable check interval and confirmation count
- Prevents false positives from transient network issues
- Audit logging between verification stages

## Monitoring & Logs

Access logs through:
```bash
# Container logs (stdout/stderr)
docker compose logs -f

# Application logs (persistent volume)
tail -f logs/shutdown_script.log

# Cron execution logs
tail -f logs/cron.log
```

## Troubleshooting Guide

### Common Issues
1. **WebSocket Connection Failures**
   - Verify SSL configuration matches TrueNAS setup
   - Check firewall rules for port 443/80 access
   - Test connectivity: `nc -zv {TRUENAS_HOST} {PORT}`

2. **Authentication Errors**
   - Confirm API user has system privileges
   - Verify credentials with TrueNAS web UI
   - Check special characters in passwords

3. **Power Check Failures**
   - Validate POWER_CHECK_URL accessibility:
     ```bash
     curl -Iv ${POWER_CHECK_URL}
     ```
   - Test endpoint response codes
   - Verify network connectivity between containers

4. **Log Rotation Issues**
   - Check filesystem permissions on log directory
   - Verify available disk space
   - Monitor log size with:
     ```bash
     du -h logs/shutdown_script.log
     ```

## Security Considerations

1. By default, TrueNAS is configured configured to use local CA for SSL certificate and so the SSL verification is disabled for SSL connections. For production use, the following should be configured: 
       * Change the shutdown-script.py to use the SSL verification. This can be done by adding the following to shutdown_script/shutdown script:

         ```python
         ssl_context = ssl.SSLContext(protocol=PROTOCOL_TLSv1) if use_ssl else None
         uri = f"wss://{host}/websocket" if use_ssl else f"ws://{host}/websocket"
         print(f"Using {'SSL' if use_ssl else 'Non-SSL'} connection: {uri}")
         ```
2. Create dedicated API user with minimum required privileges
3. Store sensitive credentials in Docker secrets (recommended for production)
4. Regularly rotate API credentials
5. Maintain separate network zones for management traffic

## Maintenance

Update dependencies:
```bash
docker compose build --no-cache
docker compose up -d --force-recreate
```
