# MCU for Data Collection Component (DCC)

# MCU is client-side, sends HTTP request to server over local network
# MCU POST to server and GET data from server and other pico

# access environmental variables stored on board in settings.toml file
import os
import wifi
import socketpool
import ssl
import adafruit_requests as requests
import time
import board
import analogio
import digitalio
import adafruit_am2320
import adafruit_bme680
import busio
import math

TIMEOUT = 30
API_KEY = os.getenv("API_KEY")
headers = {"API-Key": API_KEY}

SSID, PASSWORD = os.getenv("WIFI_SSID"), os.getenv("WIFI_PASSWORD")
BASE_URL = "http://172.20.10.11:8000/"


def init() -> None:
    """
    Initializes and configures all sensors connected to the MCU.

    Sets up the following hardware:
        - Thermistor (A1): Analog temperature sensor powered via GP16 to prevent self-heating when idle.
        - Gas sensor (A0): Analog air quality sensor.
        - BME680 (I2C: SCL=GP19, SDA=GP18): Temperature, humidity, pressure, and gas resistance sensor.
        - AM2320 (I2C: SCL=GP1, SDA=GP0): Temperature and humidity sensor.
    """
    global control_pin, thermistor, gas_sensor, i2c_bme, bme680_sensor, i2c_am, am2320_sensor
    # global pir

    # Set a control GPIO pin for power to thermistor
    control_pin = digitalio.DigitalInOut(board.GP16)
    control_pin.direction = (
        digitalio.Direction.OUTPUT
    )  # sends 3.3V to power circuit if True
    control_pin.value = (
        False  # start with the power off to avoid self-heating of thermistor
    )

    # Set up analog input using pin connected to thermistor
    thermistor = analogio.AnalogIn(board.A1)

    # Set up analog input using pin connected to gas sensor
    gas_sensor = analogio.AnalogIn(board.A0)

    # I2C for BME680 sensor
    i2c_bme = busio.I2C(scl=board.GP19, sda=board.GP18)
    bme680_sensor = adafruit_bme680.Adafruit_BME680_I2C(i2c_bme, address=0x76)

    # I2C for AM2320 sensor
    i2c_am = busio.I2C(scl=board.GP1, sda=board.GP0)
    am2320_sensor = adafruit_am2320.AM2320(i2c_am)

    # Set up PIR, Commented out due to the redundancy of the boolean reading it provides
    # pir = digitalio.DigitalInOut(board.GP15)
    # pir.direction = digitalio.Direction.INPUT


def main() -> None:
    """
    Connects to WiFi, establishes an HTTP session, `/render.pem` stores the certification
    Enters an infinite while loop that reads and transmits sensor data every
    10 seconds. Each iteration collects temperature, humidity, and gas readings
    and posts them to both the server and the SDS MCU, then retrieves any
    pending data from each.
    """
    global control_pin, thermistor, gas_sensor, i2c_bme, bme680_sensor, i2c_am, am2320_sensor
    # global pir

    wifi.radio.connect(SSID, PASSWORD)
    print("Connected:", wifi.radio.ipv4_address)

    # reads pem file and stores it as string in cert_data variable
    with open("/render.pem", "rb") as f:
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
                "temperature": thermistor_temp_C(),
                "humidity": am2320_sensor.relative_humidity,
                # "pir": pir.value,
                "gas": gas_sensor.value,
                "id": "mcu_sensor_box",
                "time": time.time(),
                "location": 0.0,
                "status": "on",
            }

            post_server(http, sensor_readings)
            post_mcu_arm(http, sensor_readings)
            get_server(http)
            get_mcu_arm(http)


def thermistor_temp_C(R0=10000.0, T0=25.0, B=3950.0):
    """
    Calculates the temperature in Celsius from the raw thermistor data
    using the B coefficient Steinhart-Hart equation
    """

    control_pin.value = True  # turn power on to read temperature

    try:  # error handling for division by 0 and value error due to thermistor.value
        thermistor_resistance = 10000 / (
            65535 / thermistor.value - 1
        )  # thermistor resistance in ohms
        steinhart = math.log(thermistor_resistance / R0) / B + 1.0 / (
            T0 + 273.15
        )  # find 1/T
        temp = (1.0 / steinhart) - 273.15  # find T in celcius
    except (ZeroDivisionError, ValueError):
        control_pin.value = False
        return None

    control_pin.value = False  # turn power off to save battery and prevent self heating
    return temp


"""
The following functions make varying POST or GET http requests to the server.
Each http request is sent with 'headers' including the API-Key and a defined
TIMEOUT value of 30 seconds to ensure the promise is not waiting indefinitely
to be fulfilled and a 408 timeout error code will be thrown.
In case of off-chance errors, each http call is tried up to 5 times before
an error status code is thrown.
"""


# sensor_readings (dict) are POSTED to server and appended to server queue
def post_server(http, sensor_readings) -> None:
    data = {
        "to": "server",
        "data": sensor_readings,
    }

    for _ in range(5):
        response = http.post(
            f"{BASE_URL}/receive",
            json=data,
            headers=headers,
            timeout=TIMEOUT,
        )
        response_dictionary = response.json()

        if response_dictionary.get("status_code") == 200:
            break

    print(response_dictionary.get("status_code"))

    if response_dictionary.get("status_code") != 200:
        print(response_dictionary.get("message"))

    response.close()


# sensor_readings (dict) are POSTED to server and appended to MCU queue specified by `to`
def post_mcu_arm(http, sensor_readings) -> None:
    data = {
        "to": "mcu_arm",
        "data": sensor_readings,
    }

    for _ in range(5):
        response = http.post(
            f"{BASE_URL}/receive",
            json=data,
            headers=headers,
            timeout=TIMEOUT,
        )
        response_dictionary = response.json()

        if response_dictionary.get("status_code") == 200:
            break

    print(response_dictionary.get("status_code"))

    if response_dictionary.get("status_code") != 200:
        print(response_dictionary.get("message"))

    response.close()


# Data is requested from server queue
def get_server(http) -> None:
    for _ in range(5):
        response = http.get(
            f"{BASE_URL}/get_server_data",
            headers=headers,
            timeout=TIMEOUT,
        )
        response_dictionary = response.json()

        if response_dictionary.get("status_code") == 200:
            break

    print(response_dictionary.get("status_code"))

    if response_dictionary.get("status_code") != 200:
        print(response_dictionary.get("message"))
    else:
        print(response_dictionary.get("data"))

    response.close()


# Data is requested from MCU queue specified by `target`
def get_mcu_arm(http) -> None:
    target_dictionary = {
        "target": "mcu_arm",
    }

    for _ in range(5):
        response = http.post(
            f"{BASE_URL}/get_mcu_data",
            json=target_dictionary,
            headers=headers,
            timeout=TIMEOUT,
        )
        response_dictionary = response.json()

        if response_dictionary.get("status_code") == 200:
            break

    print(response_dictionary.get("status_code"))

    if response_dictionary.get("status_code") != 200:
        print(response_dictionary.get("message"))
    else:
        print(f"Data from mcu_arm: {response_dictionary.get('data')}")

    response.close()


if __name__ == "__main__":
    main()
