import base64
import io
from pathlib import Path

import numpy as np
from flask import Flask, jsonify, request, send_from_directory
from PIL import Image, ImageOps, UnidentifiedImageError

from matrix_operations import (
    adjust_brightness,
    flip_horizontal,
    to_black_white,
    to_grayscale,
)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024


@app.get("/")
def home():
    return send_from_directory(Path(__file__).parent / "public", "index.html")


@app.post("/api/process")
def process_image():
    uploaded = request.files.get("image")
    if uploaded is None or not uploaded.filename:
        return jsonify(error="Choose an image first."), 400

    try:
        with Image.open(uploaded.stream) as source:
            image = ImageOps.exif_transpose(source).convert("RGB")
            image.thumbnail((1200, 1200))
            rgb = np.asarray(image, dtype=np.uint8)

        operation = request.form.get("op", "grayscale")
        if operation == "grayscale":
            result = to_grayscale(rgb)
        elif operation == "brightness":
            result = adjust_brightness(rgb, int(request.form.get("brightness", 0)))
        elif operation == "flip":
            result = flip_horizontal(rgb)
        elif operation == "bw":
            result = to_black_white(rgb, int(request.form.get("threshold", 128)))
        else:
            return jsonify(error="Choose a valid operation."), 400

        def png_data_url(array):
            buffer = io.BytesIO()
            Image.fromarray(np.ascontiguousarray(array)).save(buffer, format="PNG")
            encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
            return f"data:image/png;base64,{encoded}"

        return jsonify(original=png_data_url(rgb), result=png_data_url(result))

    except (UnidentifiedImageError, OSError):
        return jsonify(error="That file is not a valid image."), 400
    except ValueError:
        return jsonify(error="Enter valid numeric settings."), 400


@app.errorhandler(413)
def file_too_large(_error):
    return jsonify(error="Image is too large. The maximum file size is 10 MB."), 413


if __name__ == "__main__":
    app.run(debug=True)
