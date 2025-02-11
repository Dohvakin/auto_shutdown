# TrueNAS Automated Shutdown System

A Dockerized service that monitors power status and initiates graceful TrueNAS shutdowns via WebSocket API.

## Project Structure

Key files:
- `shutdown_script.py` - Main Python logic for power checks and shutdown
- `entrypoint.sh` - Container entrypoint that sets up cron
- `Dockerfile` - Builds the container image with Python 3.11
- `docker-compose.yaml` - Docker configuration with environment variables
- `crontab` - Cron schedule configuration
- `pyproject.toml` - Python dependencies specification
- `uv.lock` - Pinned dependency versions
- `run_script.sh` - Helper script for manual execution

## Features

- Real-time power monitoring via HTTP endpoint
- Configurable grace period with multiple verification checks
- Secure WebSocket communication with TrueNAS
- Detailed logging (container and persistent filesystem)
- Cron-based scheduling inside Docker container
- Dependency management with UV/Pip-Tools

## Requirements

- Docker 20.10+
- Python 3
- TrueNAS Scale
- Network-accessible power monitoring endpoint (this should accept a GET request)

## Installation

1. Clone repository:
```bash
git clone https://github.com/Dohvakin/auto_shutdown
cd auto_shutdown
```

2.  **Configure Environment Variables:**  You can configure the service by adjusting the environment variables directly within the `docker-compose.yaml` file.  There's no need to create a separate `.env` file.  Open `docker-compose.yaml` in a text editor.

3.  **Edit the `environment:` section:**  Within the `truenas-shutdown` service definition, you'll find an `environment:` section.  Modify the values on the right-hand side of each line to match your TrueNAS setup:


```yaml
environment:
   TRUENAS_HOST: "your_truenas_url:port"  # e.g., 192.168.1.100:443
   TRUENAS_USERNAME: "admin"           # Your TrueNAS admin username
   TRUENAS_PASSWORD: "admin_password"    # Your TrueNAS admin password
   USE_SSL: "true"                     # Set to "false" if not using HTTPS
   INTERVAL_CHECK_ENABLED: "false"       # Set to "true" for if want to check power status every 5 minutes
   POWER_CHECK_URL: "http://192.168.1.11"  # URL to check power status
   CHECK_INTERVAL: "60"                # Interval in seconds between checks (if INTERVAL_CHECK_ENABLED is true)
   TOTAL_CHECKS: "5"                  # Number of checks before shutdown (if INTERVAL_CHECK_ENABLED is true)
```

   *   **Important:** Replace the placeholder values (`your_truenas_url:port`, `admin`, `admin_password`, `http://192.168.1.11`) with your actual TrueNAS connection details and power monitoring endpoint.  Be sure to include the port number (usually `443` for HTTPS, `80` for HTTP) in the `TRUENAS_HOST`.
   *  If your endpoint uses `https` keep `USE_SSL=true`. If your endpoint uses `http` change the `USE_SSL` field to `false`.
   *   `POWER_CHECK_URL`:  **This is crucial.**  Change this to the URL of your power monitoring device.  The script will make a GET request to this URL.  A 200 response code means power is ON.  Anything else (including a timeout) is considered a power failure.
   *   `CHECK_INTERVAL` and `TOTAL_CHECKS`:  These control the behavior when `INTERVAL_CHECK_ENABLED` is set to `true`.

4.  **Modify Power Monitoring URL (if not using environment variables):**  If you are *not* using environment variables for the power check URL (not recommended), you will need to edit the `shutdown_script.py` file directly.  Find the line `power_check_url = "http://192.168.1.11"` and change it to the correct URL.  It is *highly recommended* to use the environment variable in `docker-compose.yaml` instead.

5. Build the Docker image and start services:
```bash
docker-compose build  # Constructs image using the Dockerfile in this directory
docker-compose up -d  # Starts container in background
```

## Configuration

### Environment Variables

| Variable                | Default     | Description                                                                   |
|-------------------------|-------------|-------------------------------------------------------------------------------|
| TRUENAS_HOST            | -           | TrueNAS host:port (required)                                                  |
| TRUENAS_USERNAME        | -           | API username (required)                                                       |
| TRUENAS_PASSWORD        | -           | API password (required)                                                       |
| USE_SSL                 | true        | Enable HTTPS for WebSocket connection                                          |
| INTERVAL_CHECK_ENABLED  | false       | Enable multi-verification shutdown logic                                      |
| POWER_CHECK_URL         | -          | URL to check power status (required)                                        |
| CHECK_INTERVAL          | 60          | Interval in seconds between checks (if `INTERVAL_CHECK_ENABLED` is true)       |
| TOTAL_CHECKS            | 5          | Number of checks before shutdown (if `INTERVAL_CHECK_ENABLED` is true)         |

### Cron Configuration

The `crontab` file controls execution schedule:
```cron
* * * * * /usr/src/app/run_script.sh >> /usr/src/app/logs/cron.log 2>&1
```

## Dependencies

**Note:** These are only required if you intend to develop on the script.  For regular usage, the Docker setup contains all dependencies and Python environment configured automatically.

Managed via UV/Pip-Tools:
- Python 3.12 base
- websockets
- requests
- pytz

To update dependencies:
```bash
pip install uv #if not installed already
uv sync
```
## Monitoring

View logs via:
```bash
# Container logs
docker logs -f truenas-shutdown-cron

# Persistent logs (inside the container's volume)
tail -f logs/shutdown.log
```

## Operational Modes

1. **Immediate Shutdown** (INTERVAL_CHECK_ENABLED=false):
   - Single power check
   - Immediate shutdown if failure detected

2. **Verified Shutdown** (INTERVAL_CHECK_ENABLED=true):
   - Checks power status every $CHECK_INTERVAL seconds
   - Requires $TOTAL_CHECKS consecutive failures
   - Sends warning to TrueNAS audit log before shutdown (Future Enhancement)

## Troubleshooting

Common issues:
- WebSocket connection failures: Verify SSL settings and firewall rules
- Cron not executing: Check `logs/cron.log`
- Authentication errors: Validate credentials in `.env`
- Dependency issues: Rebuild with `uv pip install -r uv.lock`
- Power check URL errors: Ensure POWER_CHECK_URL is correctly configured and accessible.
