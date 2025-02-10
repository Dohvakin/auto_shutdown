import asyncio
import websockets
import json
import ssl
import requests
from datetime import datetime, timezone
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
    """
    try:
        size = os.path.getsize(file_path)
        return size if size != 0 else 0
    except FileNotFoundError:
        return 0
    except Exception:
        return 0

async def shutdown_truenas():
    """
    Shuts down the TrueNAS system at `host` using WebSocket middleware calls,
    reading creds from environment variables.
    """
    host = os.getenv("TRUENAS_HOST", "192.168.1.22:444")
    username = os.getenv("TRUENAS_USERNAME", "testing")
    password = os.getenv("TRUENAS_PASSWORD", "testing")
    use_ssl_str = os.getenv("USE_SSL", "true")  # "true" or "false"

    # Convert string to boolean
    use_ssl = (use_ssl_str.lower() == "true")

    if use_ssl:
        # For HTTPS with a self-signed cert, create an unverified context
        ssl_context = ssl._create_unverified_context()
        uri = f"wss://{host}/websocket"
        print("Using SSL:", uri)
    else:
        ssl_context = None
        uri = f"ws://{host}/websocket"
        print("Not Using SSL:", uri)

    async with websockets.connect(uri, ssl=ssl_context) as ws:
        # 1) Handshake
        connect_msg = {
            "msg": "connect",
            "version": "1",
            "support": ["1", "pre2", "pre1"]
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
        login_parsed = json.loads(login_response)
        if login_parsed.get("error"):
            print("Authentication error:", login_parsed["error"])
            return

        # 3) Shutdown
        shutdown_msg = {
            "id": session_id,
            "msg": "method",
            "method": "system.shutdown",
            "params": []
        }
        await ws.send(json.dumps(shutdown_msg))

        # 4) Attempt to read final response
        try:
            shutdown_response = await asyncio.wait_for(ws.recv(), timeout=5)
            print("Shutdown Response:", shutdown_response)
        except asyncio.TimeoutError:
            print("No response — TrueNAS likely shutting down...")

def check_power_and_maybe_shutdown():
    power_check_url = "http://192.168.1.11"
    interval_enabled = os.environ.get('INTERVAL_CHECK_ENABLED') is not None

    if interval_enabled:
        total_checks = 5
        check_interval = 60

        for _ in range(total_checks):
            try:
                response = requests.get(power_check_url, timeout=5)
                if response.status_code == 200:
                    current_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %I:%M:%S %p %Z')
                    print(f"Electricity is on, doing nothing. Datetime: {current_time}")
                    if get_file_size("/usr/src/app/logs/shutdown_script.log") > 52428800:
                        os.remove("/usr/src/app/logs/shutdown_script.log")
                    exit()
                else:
                    print("Electricity check did not return 200 status. Will check again shortly...")
            except requests.RequestException:
                print("Error checking electricity. Possibly off. Will check again shortly...")

            time.sleep(check_interval)

        print("Power check failed multiple times. Initiating shutdown...")
        asyncio.run(shutdown_truenas())
    else:
        try:
            response = requests.get(power_check_url, timeout=5)
            if response.status_code == 200:
                current_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %I:%M:%S %p %Z')
                print(f"Electricity is on, doing nothing. Datetime: {current_time}")
                if get_file_size("/usr/src/app/logs/shutdown_script.log") > 52428800:
                    os.remove("/usr/src/app/logs/shutdown_script.log")
                exit()
            else:
                print("Electricity not detected. Initiating shutdown immediately.")
                asyncio.run(shutdown_truenas())
        except requests.RequestException:
            print("Error checking electricity, possibly off. Initiating shutdown immediately.")
            asyncio.run(shutdown_truenas())

if __name__ == "__main__":
    print("Starting shutdown script...")
    check_power_and_maybe_shutdown()