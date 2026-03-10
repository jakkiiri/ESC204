# MCU for arm

import os
import wifi
import socketpool
import json
import adafruit_requests as requests


SSID, PASSWORD = os.getenv("WIFI_SSID", "WIFI_PASSWORD")
BASE_URL = "http://127.0.0.1:5000"


def main() -> None:
    wifi.radio.connect(SSID, PASSWORD)

    pool = socketpool.SocketPool(wifi.radio)
    http = requests.Session(pool)

    data = {"testing": 0}

    response = http.post(f"{BASE_URL}/receive", data=json.dumps(data))

    print(response)


if __name__ == "__main__":
    main()
