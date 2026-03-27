# MCU for arm

import os  # access environmental variables stored on board in settings.toml file
import wifi
import socketpool
import ssl
import adafruit_requests as requests
import time

TIMEOUT = 30
API_KEY = os.getenv("API_KEY")
headers = {"API-Key": API_KEY}

SSID, PASSWORD = os.getenv("WIFI_SSID"), os.getenv("WIFI_PASSWORD")
BASE_URL = "https://active-fire-monitoring-esc204.onrender.com/"


def main() -> None:
    wifi.radio.connect(SSID, PASSWORD)
    print("Connected:", wifi.radio.ipv4_address)

    # reads pem file and stores it as string in cert_data variable
    with open("/render.pem", "r") as f:
        cert_data = f.read()

    pool = socketpool.SocketPool(wifi.radio)
    ssl_context = ssl.create_default_context()
    ssl_context.load_verify_locations(cadata=cert_data)
    http = requests.Session(pool, ssl_context)

    sensor_readings = {
        "temperature": 0,
        "humidity": 0,
        "battery": 0,
    }
    post_server(http, sensor_readings)


def post_server(http, sensor_readings) -> None:
    data = {
        "to": "server",
        "data": sensor_readings,
    }

    # calls server up to 5 times, and if don't break early then checks on the 5th time
    response_dictionary = {}
    count = 0
    while response_dictionary.get("status_code") != 200 and count < 5:
        response = http.post(
            f"{BASE_URL}/receive",
            json=data,
            headers=headers,
            timeout=TIMEOUT,
        )
        response_dictionary = response.json()
        count += 1

    print(response_dictionary.get("status_code"))

    if response_dictionary.get("status_code") != 200:
        print(response_dictionary.get("message"))

    response.close()


if __name__ == "__main__":
    main()
