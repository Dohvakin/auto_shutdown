import asyncio
import websockets
import json
import ssl
import requests
from datetime import datetime
import time
import pytz
import os

def get_file_size(file_path) -> int:
    """
    This function returns the size of a file in bytes.
    If the file does not exist, it returns 0.
    If there is an error, it returns 0.

    args:
        file_path (str): The path to the file.

    output:
        int: The size of the file in bytes.
    """
    try:
        return os.path.getsize(file_path)
    except (FileNotFoundError, OSError):
        return 0

async def shutdown_truenas(host, username, password, use_ssl) -> None:
    """
    Shuts down the TrueNAS system using WebSocket middleware calls.
    args:
        host (str): The hostname or IP address of the TrueNAS system.
        username (str): The username for the TrueNAS system.
        password (str): The password for the TrueNAS system.
        use_ssl (bool): Whether to use SSL for the connection.
    """
    ssl_context = ssl._create_unverified_context() if use_ssl else None
    uri = f"wss://{host}/websocket" if use_ssl else f"ws://{host}/websocket"
    print(f"Using {'SSL' if use_ssl else 'Non-SSL'} connection: {uri}")

    async with websockets.connect(uri, ssl=ssl_context) as ws:
        # 1) Handshake
        connect_msg = {
                "msg": "connect",
                "version": "1",
                "support": ["1","pre2","pre1"]
        }
        await ws.send(json.dumps(connect_msg))
        connect_response = await ws.recv()
        session_id = json.loads(connect_response).get("session")
        print("Connect Response:", connect_response)

        # 2) Authenticate
        login_msg = {
                "id": session_id,
                "msg": "method",
                "method": "auth.login",
                "params": [username, password]
        }
        await ws.send(json.dumps(login_msg))
        login_response = await ws.recv()
        print("Login Response:", login_response)
        if json.loads(login_response).get("error"):
            print("Authentication error:", json.loads(login_response)["error"])
            return

        # 3) Shutdown
        shutdown_msg = {
                "id": session_id,
                "msg": "method",
                "method": "system.shutdown",
                "params": []
        }
        await ws.send(json.dumps(shutdown_msg))

        # 4) Attempt to read final response (optional)
        try:
            shutdown_response = await asyncio.wait_for(ws.recv(), timeout=5)
            print("Shutdown Response:", shutdown_response)
        except asyncio.TimeoutError:
            print("No response — TrueNAS likely shutting down...")

def check_power_and_maybe_shutdown():
    """
    Checks power status and initiates TrueNAS shutdown if necessary.
    """
    power_check_url = os.getenv("POWER_CHECK_URL", "192.168.1.11")
    interval_enabled = os.getenv("INTERVAL_CHECK_ENABLED", "false").lower() == "true"
    total_checks = int(os.getenv("TOTAL_CHECKS", "5"))  # Default to 5 checks
    check_interval = int(os.getenv("CHECK_INTERVAL", "60"))  # Default to 60 seconds
    truenas_host = os.getenv("TRUENAS_HOST")
    truenas_username = os.getenv("TRUENAS_USERNAME")
    truenas_password = os.getenv("TRUENAS_PASSWORD")
    use_ssl = os.getenv("USE_SSL", "true").lower() == "true"
    log_file_path = "/usr/src/app/logs/shutdown_script.log" # Default to TrueNAS host. Change if needed



    def log_and_check_size(message:str) -> None:
        """
        This function logs the message and checks the size of the log file.
        If the file size exceeds 50MB, it deletes the file.

        args:
            message (str): The message to log.
        """
        timezone_ist = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(timezone_ist).strftime('%Y-%m-%d %I:%M:%S %p %Z')
        print(f"{message}. Datetime: {current_time}")
        if get_file_size(log_file_path) > 52428800:  # 50MB
             try:
                 os.remove(log_file_path)
             except OSError as e:
                print(f"Error deleting log file: {e}")


    if not all([power_check_url, truenas_host, truenas_username, truenas_password]):
        print("Error: Required environment variables \
            (POWER_CHECK_URL, TRUENAS_HOST, TRUENAS_USERNAME, TRUENAS_PASSWORD) are not set.")
        return

    for _ in range(total_checks if interval_enabled else 1):
        try:
            response = requests.get(power_check_url, timeout=5)
            if response.status_code == 200:
                log_and_check_size("Electricity is on, doing nothing")
                return  # Exit if power is ON

            log_and_check_size("Electricity check did not return 200 status. Will check again shortly" if interval_enabled else "Electricity not detected. Initiating shutdown immediately")

        except requests.RequestException as e:
            log_and_check_size(f"Error checking electricity: {e}.  Will check again shortly" if interval_enabled else f"Error checking electricity {e}. Initiating shutdown immediately")
        except Exception as e:
            # Handle other exceptions
            log_and_check_size(f"Unknown error: {e}.  Will check again shortly" if interval_enabled else f"Unknown error: {e}. Will shutdown immediately")

        if interval_enabled:
            time.sleep(check_interval)

    print("Power check failed. Initiating shutdown...")
    # Shutdown the system here using Truenas API or other methods
    asyncio.run(shutdown_truenas(truenas_host, truenas_username, truenas_password, use_ssl))

if __name__ == "__main__":
    print("Starting the script...")

    check_power_and_maybe_shutdown()