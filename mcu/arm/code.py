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
BASE_URL = "https://active-fire-monitoring-esc204.onrender.com"


def main() -> None:
    wifi.radio.connect(SSID, PASSWORD)
    print("Connected:", wifi.radio.ipv4_address)

    # reads pem file and stores it as string in cert_data variable
    with open("/render.pem", "r") as f:
        cert_data = f.read()

    # creates network session
    pool = socketpool.SocketPool(wifi.radio)
    ssl_context = ssl.create_default_context()
    ssl_context.load_verify_locations(cadata=cert_data)
    http = requests.Session(pool, ssl_context)

    last_time = time.time()

    while True:
        current_time = time.time()
        if current_time > last_time + 10:
            last_time = time.time()
            sensor_readings = {
                "temperature": 0,
                "humidity": 0,
                "battery": 0,
            }
            post_server(http, sensor_readings)
            post_mcu_arm(http, sensor_readings)
            get_server(http)
            get_mcu_arm(http)


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


def post_mcu_arm(http, sensor_readings) -> None:
    data = {
        "to": "mcu_sensor_box",
        "data": sensor_readings,
    }

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


def get_server(http) -> None:
    response_dictionary = {}
    count = 0
    while response_dictionary.get("status_code") != 200 and count < 5:
        response = http.get(
            f"{BASE_URL}/get_server_data",
            headers=headers,
            timeout=TIMEOUT,
        )
        response_dictionary = response.json()
        count += 1
    
    print(response_dictionary.get("status_code"))

    if response_dictionary.get("status_code") != 200:
        print(response_dictionary.get("message"))
    else:
        print(response_dictionary.get("data"))

    response.close()


def get_mcu_arm(http) -> None:
    target_dictionary = {
        "target": "mcu_sensor_box",
    }

    response_dictionary = {}
    count = 0
    while response_dictionary.get("status_code") != 200 and count < 5:
        response = http.post(
            f"{BASE_URL}/get_mcu_data",
            json=target_dictionary,
            headers=headers,
            timeout=TIMEOUT,
        )
        response_dictionary = response.json()
        count += 1

    print(response_dictionary.get("status_code"))

    if response_dictionary.get("status_code") != 200:
        print(response_dictionary.get("message"))
    else:
        print(response_dictionary.get("data"))

    response.close()


if __name__ == "__main__":
    main()
