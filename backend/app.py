from flask import Flask, request, jsonify, Response

app = Flask(__name__)


@app.route("/")
def home() -> str:
    return "Server is running"


@app.route("/compute", methods=["POST"])
def compute_from_data() -> Response:
    data = request.json

    # perform computations with data

    return jsonify({"sample_response": 0})


@app.route("/plan_route", methods=["GET"])
def get_route() -> Response:
    # perform necessary computations here

    return jsonify({"sample_response": 0})


if __name__ == "__main__":
    app.run()
