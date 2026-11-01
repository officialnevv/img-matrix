import base64
import io
import os
import sys

import numpy as np
from flask import Flask, jsonify, request, send_from_directory
from PIL import Image

app = Flask(__name__)


def load_image(file, max_side=1200):
    img = Image.open(file).convert("RGB")
    img.thumbnail((max_side, max_side))
    return np.asarray(img, dtype=np.uint8)


def to_grayscale(rgb):
    weights = np.array([0.299, 0.587, 0.114])
    return np.rint(rgb.astype(np.float64) @ weights).astype(np.uint8)


def adjust_brightness(img, beta):
    return np.clip(img.astype(np.int16) + int(beta), 0, 255).astype(np.uint8)


def flip_horizontal(img):
    return img[:, ::-1]


def flip_horizontal_matrix(img):
    J = np.eye(img.shape[1])[::-1]
    if img.ndim == 3:
        out = np.einsum("hwc,wv->hvc", img.astype(np.float64), J)
    else:
        out = img @ J
    return np.rint(out).astype(np.uint8)


def to_black_white(rgb, threshold=128):
    return np.where(to_grayscale(rgb) >= threshold, 255, 0).astype(np.uint8)


def to_data_url(arr):
    buf = io.BytesIO()
    Image.fromarray(np.ascontiguousarray(arr)).save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def apply_operation(rgb, op, brightness=0, threshold=128):
    if op == "grayscale":
        return to_grayscale(rgb)
    if op == "brightness":
        return adjust_brightness(rgb, brightness)
    if op == "flip":
        return flip_horizontal(rgb)
    if op == "bw":
        return to_black_white(rgb, threshold)
    raise ValueError("unknown operation: " + op)


@app.route("/")
def home():
    return send_from_directory("public", "index.html")


@app.route("/api/process", methods=["POST"])
def process():
    file = request.files.get("image")
    if file is None:
        return jsonify(error="No image uploaded"), 400
    try:
        rgb = load_image(file)
        result = apply_operation(
            rgb,
            request.form.get("op", "grayscale"),
            int(request.form.get("brightness", 0)),
            int(request.form.get("threshold", 128)),
        )
    except Exception as e:
        return jsonify(error=str(e)), 400
    return jsonify(original=to_data_url(rgb), result=to_data_url(result))


def run_local(path, beta=50, threshold=128):
    import matplotlib.pyplot as plt

    rgb = load_image(path)
    results = [
        ("original", rgb),
        ("grayscale", to_grayscale(rgb)),
        ("brightness", adjust_brightness(rgb, beta)),
        ("flip", flip_horizontal(rgb)),
        ("black_white", to_black_white(rgb, threshold)),
    ]

    os.makedirs("output", exist_ok=True)
    fig, axes = plt.subplots(1, len(results), figsize=(4 * len(results), 4))
    for ax, (name, arr) in zip(axes, results):
        ax.imshow(arr, cmap="gray" if arr.ndim == 2 else None, vmin=0, vmax=255)
        ax.set_title(name)
        ax.axis("off")
        Image.fromarray(np.ascontiguousarray(arr)).save(os.path.join("output", name + ".png"))
    plt.tight_layout()
    plt.savefig(os.path.join("output", "comparison.png"))
    plt.show()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        beta = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        threshold = int(sys.argv[3]) if len(sys.argv) > 3 else 128
        run_local(sys.argv[1], beta, threshold)
    else:
        app.run(debug=True)
