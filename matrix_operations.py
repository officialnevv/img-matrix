import numpy as np


def to_grayscale(rgb):
    weights = np.array([0.299, 0.587, 0.114])
    gray = rgb.astype(np.float64) @ weights
    return np.rint(gray).astype(np.uint8)


def adjust_brightness(img, beta):
    result = img.astype(np.int32) + int(beta)
    return np.clip(result, 0, 255).astype(np.uint8)


def flip_horizontal(img):
    width = img.shape[1]
    J = np.eye(width)[::-1]

    if img.ndim == 2:
        flipped = img @ J
    else:
        channels = [
            img[:, :, c] @ J
            for c in range(img.shape[2])
        ]
        flipped = np.stack(channels, axis=2)

    return flipped.astype(np.uint8)


def to_black_white(rgb, threshold=128):
    gray = to_grayscale(rgb)
    binary = np.where(gray >= threshold, 255, 0)
    return binary.astype(np.uint8)
