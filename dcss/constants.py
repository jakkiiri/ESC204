"""
Initialize global constants used in dcss/app.py
"""

MCU_SENSOR_BOX = "mcu_sensor_box"
MCU_ARM = "mcu_arm"
SERVER = "server"

DATABASE_PATH = "database/history.db"

API_KEY_ID = "API-Key"

MAX_ARRAY_LENGTH = 100000000

MALFORMED_REQUEST_BODY_DEFAULT_REPONSE = {
    "status": "error",
    "status_code": 400,
    "message": "Malformed request body",
}

UNAUTHORIZED_DEFAULT_RESPONSE = {
    "status": "error",
    "status_code": 401,
    "message": "Unauthorized",
}
