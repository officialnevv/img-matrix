# Image Processing Using Matrices

Linear Algebra project. An image is a matrix of pixel values (0-255); a colour image is H x W x 3 (R, G, B). The Python code is in one file, `app.py` (Python + NumPy). The web page is `public/index.html`.

| Operation | Formula | NumPy |
|---|---|---|
| Grayscale | `Gray = 0.299R + 0.587G + 0.114B` | `rgb @ [0.299, 0.587, 0.114]` |
| Brightness | `I' = clip(I + b, 0, 255)` | `np.clip(img + beta, 0, 255)` |
| Horizontal flip | `I' = I . J` (J = exchange matrix) | `img[:, ::-1]` |
| Black & white | `B = 255 if Gray >= T else 0` | `np.where(gray >= T, 255, 0)` |

## Run on your computer
```
pip install -r requirements.txt -r requirements-local.txt
python app.py image.jpg 50 128
```
Shows the original next to every result and saves them in `output/` (50 = brightness, 128 = threshold).

## Run the website locally
```
python app.py
```
Then open http://127.0.0.1:5000

## Deploy on Vercel
Push to GitHub, import the repo at vercel.com/new, click Deploy. Vercel finds the Flask app in `app.py` and serves the page from `public/`. Uploads must be under about 4.5 MB.
