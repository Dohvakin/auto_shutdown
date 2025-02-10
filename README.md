# TrueNAS Shutdown Service

A system service that periodically checks power status and can initiate a shutdown of TrueNAS via its WebSocket API.

## Description

The TrueNAS Shutdown Service is a containerized application that:
- Periodically checks power status via a configured endpoint
- Initiates a graceful shutdown of TrueNAS if power status goes out
- Uses WebSocket API to communicate with TrueNAS
- Runs as a cron job in Docker container
- Supports interval-based power checks (if enabled)

## Setup Requirements

- Docker installed on system
- Basic understanding of Docker commands
- Access to TrueNAS system with proper credentials
- Power monitoring endpoint in place

## Installation

1. Clone this repository

```bash
git clone https://github.com/Dohvakin/auto_shutdown
cd auto_shutdown
```

2. Create a docker-compose.yaml file

```bash
TRUENAS_HOST=your_truenas_url:port
TRUENAS_USERNAME=admin
TRUENAS_PASSWORD=admin_password
USE_SSL=true/false
INTERVAL_CHECK_ENABLED=true/false 
```

3. Build and start the container

```bash
docker-compose build
docker-compose up -d
```

## Configuration Variables

The script reads the following environment variables:

| Variable                | Description                                                                                   |
|-------------------------|---------------------------------------------------------------------------------------------|
| TRUENAS_HOST            | URL of your TrueNAS server including port (e.g., 192.168.1.22:444)                            |
| TRUENAS_USERNAME        | Username for TrueNAS Web Interface                                                           |
| TRUENAS_PASSWORD        | Password for TrueNAS Web Interface                                                           |
| USE_SSL                 | Enable SSL (true/false) - should be true for production                                    |
| INTERVAL_CHECK_ENABLED  | Enable interval-based power checks (true/false). If enabled, performs checks every minute for 5 attempts before shutting down. |

## Usage

The service runs continuously checking power status. If `INTERVAL_CHECK_ENABLED` is set:
- It will check the power status every minute for up to 5 attempts before initiating a shutdown.
- If no power is detected within 5 attempts, it will shut down the system.

If `INTERVAL_CHECK_ENABLED` is not set:
- The service will check the power status once and initiate an immediate shutdown if no power is detected.

Logs are available in the container and on disk at `/usr/src/app/logs`.

To check logs:

```bash
docker logs -f truenas-shutdown-cron
```

## Notes

- The service uses WebSockets for secure communication with TrueNAS
- SSL is enabled by default
- A backup power monitoring system is recommended
- Regular testing of the shutdown procedure is advised
- When `INTERVAL_CHECK_ENABLED` is set, the service will provide multiple attempts to confirm power status before shutting down

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.