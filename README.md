# Image Processing Using Matrices

A Linear Algebra project demonstrating four image-processing operations implemented with NumPy matrix operations.

## Project structure

```text
img-matrix-main/
├── matrix_operations.py   # Core project: the four mathematical operations
├── app.py                 # Small Flask wrapper: upload, call operations, return images
├── public/
│   └── index.html          # Pixel-style browser interface
├── requirements.txt
└── README.md
```

## The actual project: `matrix_operations.py`

This is the mathematical core. It contains only:

- `to_grayscale(rgb)` — multiplies each RGB pixel by the grayscale weight vector.
- `adjust_brightness(img, beta)` — adds a brightness value and clips results to 0–255.
- `flip_horizontal(img)` — multiplies the image by the column-reversal matrix `J`.
- `to_black_white(rgb, threshold=128)` — converts to grayscale and applies a threshold.

These functions can be imported and used without Flask or the web interface.

## The wrapper: `app.py`

The Flask application does not reimplement image processing. It accepts an uploaded image, converts it into a NumPy array, calls the selected function from `matrix_operations.py`, and returns the original and processed images to the browser.

The interface is in `public/index.html`. It is only the presentation layer; it sends the selected operation and image to Flask.

## Run locally (Windows)

1. Install Python 3.12 or newer.
2. Open a terminal in the project folder.
3. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .venv\Scripts\activate
   ```

4. Install the dependencies:

   ```powershell
   py -m pip install -r requirements.txt
   ```

5. Start the app:

   ```powershell
   py app.py
   ```

6. Open `http://127.0.0.1:5000` in your browser.

## Update an existing GitHub repository

The ZIP download does not contain your repository's hidden `.git` history. The safest method is:

1. Open your existing local clone of the GitHub repository.
2. Extract this ZIP somewhere temporary.
3. Copy the contents of its `img-matrix-main` folder into your existing repository folder, replacing files when asked. Do not replace or delete the repository's hidden `.git` folder.
4. Open a terminal in the existing repository folder.

Then run these commands. They assume the GitHub remote is named `origin` and the branch is `main`:

```powershell
git status
git add -A
git commit -m "Separate matrix core and refresh pixel UI"
git push origin main
```

`git add -A` stages new files, modifications, and deletions. This is what removes the old `docs/` folder from the GitHub repository as well.

Check that the correct GitHub repository is connected:

```powershell
git remote -v
```

If no `origin` is listed, connect the repository (replace the URL with your actual GitHub URL):

```powershell
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git branch -M main
git push -u origin main
```

If Git says the remote contains commits that are not in your local folder, do not force-push. First fetch and inspect the differences:

```powershell
git fetch origin
git status
```

## Deploy on Vercel through GitHub

Vercel supports Flask applications directly. The root-level `app.py` exports the Flask instance as `app`, so this project does not need a separate `api/` folder or a custom `vercel.json` routing file.

1. Push the updated project to GitHub using the commands above.
2. Sign in to Vercel and choose **Add New → Project**.
3. Import the GitHub repository containing this project.
4. Keep the project root directory set to the folder containing `app.py` and `requirements.txt`.
5. Let Vercel detect Flask/Python. No custom build command or output directory is needed for this setup.
6. Select **Deploy**.
7. When deployment finishes, open the generated URL and test an image upload and all four operations.

After the GitHub repository is connected, pushes to the production branch (normally `main`) trigger new production deployments automatically. Other branches and pull requests can receive preview deployments.

If you already have this repository connected to a Vercel project, you normally only need to push the new commit; Vercel will deploy it automatically.

## Notes

- The app accepts image uploads up to 10 MB.
- Large images are resized so their longest side is at most 1200 pixels before processing.
- `matplotlib` is not required for the web application and has been removed from the dependencies.
- Vercel's Python runtime is used for the Flask backend; the browser interface is served by the Flask app.
