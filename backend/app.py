import json
from backend.constants import (
    MCU_SENSOR_BOX,
    MCU_ARM,
    MAX_ARRAY_LENGTH,
    SERVER,
    MALFORMED_REQUEST_BODY_DEFAULT_REPONSE,
)
from flask_cors import CORS
from flask import Flask, request, Response

app = Flask(__name__)
CORS(app)


class CommsData:

    def __init__(self) -> None:
        self.mcu: set = {MCU_ARM, MCU_SENSOR_BOX}
        self.inter_mcu: dict[str, list[dict]] = {key: [] for key in self.mcu}
        self.mcu_server: list[dict] = []

    @staticmethod
    def trim_array_length(arrays: list[list]) -> None:
        for array in arrays:
            while len(array) >= MAX_ARRAY_LENGTH:
                array.pop(0)

    def append_data(self, data: dict, target: str) -> tuple[int, str]:
        if target not in self.mcu and target != SERVER:
            return (400, f"Invalid target: {target}")

        if target == SERVER:
            self.mcu_server.append(data)
        else:
            self.inter_mcu[target].append(data)

        all_arrays: list = [self.mcu_server] + list(self.inter_mcu.values())
        CommsData.trim_array_length(all_arrays)

        return (200, "")

    def consume_data(self, target: str) -> tuple[int, str, dict]:
        if target not in self.mcu and target != SERVER:
            return (400, f"Invalid target: {target}", {})

        target_array: list = (
            self.mcu_server if target == SERVER else self.inter_mcu[target]
        )
        data: dict = {} if not target_array else target_array.pop(0)

        return (200, "", data)


comms_data = CommsData()


@app.route("/")
def home() -> str:
    return "Server is running"


@app.route("/receive", methods=["POST"])
def receive() -> Response:
    data: dict = request.get_json(silent=True) or {}

    if not data.get("to") or not data.get("data"):
        return Response(
            json.dumps(MALFORMED_REQUEST_BODY_DEFAULT_REPONSE),
            status=400,
            mimetype="application/json",
        )

    status_code, message = comms_data.append_data(data.get("data", {}), data["to"])

    return Response(
        json.dumps(
            {
                "status": "ok" if status_code == 200 else "error",
                "status_code": status_code,
                "message": message,
            }
        ),
        status=status_code,
        mimetype="application/json",
    )


@app.route("/get_mcu_data", methods=["POST"])
def get_mcu_data() -> Response:
    data: dict = request.get_json(silent=True) or {}

    if not data.get("target"):
        return Response(
            json.dumps(MALFORMED_REQUEST_BODY_DEFAULT_REPONSE),
            status=400,
            mimetype="application/json",
        )

    target: str = data["target"]
    status_code, message, return_data = comms_data.consume_data(target)

    return Response(
        json.dumps(
            {
                "status": "ok" if status_code == 200 else "error",
                "status_code": status_code,
                "message": message,
                "data": return_data,
            }
        ),
        status=status_code,
        mimetype="application/json",
    )


@app.route("/get_server_data", methods=["GET"])
def get_server_data() -> Response:
    status_code, message, return_data = comms_data.consume_data(SERVER)

    return Response(
        json.dumps(
            {
                "status": "ok" if status_code == 200 else "error",
                "status_code": status_code,
                "message": message,
                "data": return_data,
            }
        ),
        status=status_code,
        mimetype="application/json",
    )


# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=8000)
