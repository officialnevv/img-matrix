import base64
import io
from pathlib import Path

import numpy as np
from flask import Flask, jsonify, request, send_from_directory
from PIL import Image

from matrix_operations import (
    adjust_brightness,
    flip_horizontal,
    to_black_white,
    to_grayscale,
)

app = Flask(__name__)


def image_to_url(array):
    output = io.BytesIO()
    Image.fromarray(array).save(output, format="PNG")
    encoded_image = base64.b64encode(output.getvalue()).decode("utf-8")
    return "data:image/png;base64," + encoded_image


@app.route("/")
def home():
    return send_from_directory(Path(__file__).parent / "public", "index.html")


@app.route("/api/process", methods=["POST"])
def process_image():
    uploaded_image = request.files["image"]
    image = Image.open(uploaded_image).convert("RGB")
    original = np.array(image)

    operation = request.form["op"]

    if operation == "grayscale":
        result = to_grayscale(original)
    elif operation == "brightness":
        brightness = int(request.form.get("brightness", 0))
        result = adjust_brightness(original, brightness)
    elif operation == "flip":
        result = flip_horizontal(original)
    elif operation == "bw":
        threshold = int(request.form.get("threshold", 128))
        result = to_black_white(original, threshold)

    return jsonify({
        "original": image_to_url(original),
        "result": image_to_url(result)
    })


if __name__ == "__main__":
    app.run(debug=True)
