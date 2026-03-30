# ESC204 - IoT-Active-Wildfire-Monitoring

## Introduction
This repository contains all the code detailing the backend of the IoT network and server-microcontroller communication specifically for the prototype design of the MMSSS. It contains the data communication storage subsystem (DCSS), data collection component (DCC), and sensor deployment subsystem (SDS). The basic functionality of the IoT network is for the microcontrollers to send sensor data to the server and for the server to send instructional data back to the microcontrollers to facilitate effective communication of data across distances to best monitor active wildfires. The microcontroller used is the Raspberry Pi Pico W. A Pico W would be installed on the rover, to control the mechanical arm responsible for deploying the sensor boxes, and in each sensor box, so as to facilitate sending of sensor data that is representative of the conditions around where each box is deployed.

The server would be hosted over a local network run on a computer in the local town and it will receive data from the microcontrollers and store them in a separate database. 

## Major Code Components:
### Data Communication Storage Subsystem (DCSS) `dcss`
`app.py`
Code for Flask server that starts up and hosts the server over the local network. Has the following endpoints set up:
- `@app.route("/")` is the root endpoint that is at the base of the URL
- `@app.route("/receive", methods=["POST"])` is responsible for handling POST requests from the microcontrollers to the server. Will return the status code and message and also create a `.db` file to log the readings externally in the database
- `@app.route("/get_mcu_data", methods=["POST"])` is the endpoint for the microcontrollers to get data from the other microcontrollers to facilitate microcontroller-microcontroller communication
- `@app.route("/get_server_data", methods=["GET"])` is the endpoint for the microcontrollers to get data from the server to facilitate microcontroller-server communication

`constants.py`
Includes global definition of constants used in `app.py`.

`database.py`
Defines the functions `init_db()` and `log_message(to: str, data: dict)` called in `DCSS/app.py` that allows the server to store sensor data in a SQLite database. Opens a `.db` file within `database` that can be dragged into a SQLite viewer platform to visualize the sensor data.


### Data Collection Component (DCC) Microcontroller Code `mcu/dcc`
`code.py`
Fully integrated code, residing in the sensor box microcontrollers, that contains the IoT component responsible for managing the `http` requests to and from the server, and I/O code responsible for accessing the data from the wired sensor components. Runs a while loop that constantly gets the sensor readings and posts them to the server every 10 seconds:
```
sensor_readings = {
                "temperature": thermistor_temp_C(),
                "humidity": am2320_sensor.relative_humidity,
                "gas": gas_sensor.value,
                "id": "mcu_sensor_box",
                "time": time.time(),
                "location": 0.0,
                "status": "on",
            }
```
Makes `http` requests by calling these functions where http is the `Session` object:
```
post_server(http, sensor_readings)
post_mcu_sensor_box(http, sensor_readings)
get_server(http)
get_mcu_sensor_box(http)
```


### Sensor Deploying Subsystem (SDS) Microcontroller Code `mcu/sds`
`code.py`
Fully integrated code, residing on the rover, that contains the IoT component responsible for managing the `http` requests to and from the server, and I/O code responsible for controlling the linear actuator and servo motor that move the mechanical arm. Runs a while loop that polls for the release of the button that changes between states `[ROTATE_CW, ROTATE_STOP, ROTATE_CCW, ROTATE_STOP]`, and posts sensor readings to the server every 10 seconds:
```
payload = {
            "location": 0,
            "time": time.time(),
            "id": "mcu_arm",
            "status": "active",
        }
```
Makes `http` requests by calling these functions where http is the `Session` object:
```
post_server(http, sensor_readings)
post_mcu_sensor_box(http, sensor_readings)
get_server(http)
get_mcu_sensor_box(http)
```
