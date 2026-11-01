# Team Guide: Understanding the Code (No Python Needed)

**Image Processing Using Matrices: everything your team needs to explain the project to the professor**

## How to use this guide

Read sections 1 and 2 first (everyone). Then each member studies the part they will present (section 4), and everyone reads section 8 (likely questions). The professor said any student can be asked about any part, so the goal is to understand the *idea* behind each line, not to memorise it.

The golden rule for the discussion: **explain the math first, then show the line of code that does it.** The code is just the math written in a language the computer understands.

## 1. The big picture in one minute

1. A picture is a table of numbers (a matrix). Each number says how bright one tiny dot (pixel) is, from 0 (black) to 255 (white).
2. A colour picture has three such tables stacked: Red, Green, Blue.
3. Our program loads the picture into these tables, does a bit of linear algebra on them, and turns the new tables back into a picture.

The whole project in four sentences you can say to the professor:

> "We read the image as a matrix using Python and NumPy. Each operation is a matrix operation: grayscale is a weighted sum of the R, G, B matrices, brightness is adding a constant matrix with clipping, the flip is multiplication by the exchange matrix, and black and white is comparing each entry with a threshold. We then display and save the original and the result, and we also published it as a website."

## 2. Python and NumPy crash course (only what we use)

### 2.1 Python basics

| You see | It means |
| --- | --- |
| `x = 5` | Store the value 5 in a box named x. |
| `# text` | A comment. The computer ignores it; it is a note for humans. |
| `"hello"` | Text (a string). |
| `import numpy as np` | Bring in a toolbox called NumPy and call it `np` for short. |
| `def name(a, b):` | Define a function: a recipe that takes inputs a and b and gives back a result. |
| `return x` | The function's answer. |
| `if ...:` / `else:` | Do something only when a condition is true. |

Python uses **indentation** (spaces at the start of a line) to show what belongs inside a function or an if.

### 2.2 NumPy: arrays are matrices

NumPy is a library for working with whole matrices at once. Its matrix type is called an **array**.

```python
A = np.array([[10, 20, 30],
              [40, 50, 60]])
```

This is the matrix with 2 rows and 3 columns.

| Code | Meaning |
| --- | --- |
| `A.shape` | The size: (2, 3) means 2 rows, 3 columns. A colour image has shape (H, W, 3): height, width, 3 colours. |
| `A[0, 1]` | The entry in row 0, column 1 (Python counts from 0), which is 20. |
| `A[:, 0]` | The whole first column. The `:` means "everything". |
| `A + 50` | Adds 50 to every entry at once. No loop needed. |
| `A >= 30` | A matrix of True/False: is each entry at least 30? |
| `A[:, ::-1]` | All rows, and the columns in reverse order. This flips the matrix left to right. |

**Slicing `[:, ::-1]` explained.** Inside the brackets the part before the comma is for rows and the part after is for columns. `:` for rows means all rows. `::-1` for columns means "from start to end, stepping backwards by 1", so the columns come out reversed.

### 2.3 Data types (why we write `astype`)

Pictures store each number in 8 bits, called `uint8` (unsigned integer 8-bit), which can only hold 0 to 255. If you add 50 to 240 in `uint8` the answer wraps around to 34 instead of 290. So before calculations we convert to a bigger type with `.astype(...)`:

- `float64`: decimal numbers (used for grayscale, because the weights are decimals).
- `int16`: larger whole numbers, can hold values up to 32767 and negatives (used for brightness).

After calculating we convert back with `.astype(np.uint8)` so the numbers are valid pixel values.

### 2.4 Four NumPy functions you must know

| Function | What it does | Example |
| --- | --- | --- |
| `@` | Matrix multiplication / dot product. | `rgb @ w` |
| `np.clip(x, 0, 255)` | Forces every value into the range 0–255 (too big becomes 255, too small becomes 0). | clip(290) = 255 |
| `np.where(cond, a, b)` | For each entry: if the condition is true use a, otherwise b. | `np.where(g >= 128, 255, 0)` |
| `np.rint(x)` | Rounds to the nearest whole number. | rint(124.2) = 124 |

## 3. The files in the project

| File | What it is | Who needs to know it |
| --- | --- | --- |
| `app.py` | **The whole Python code in one file.** It holds the matrix operations (the heart of the project), the local program (`run_local`) and the website server (Flask). | Everyone for the matrix functions and `run_local`; web and deployment members for the server part |
| `public/index.html` | The web page the user sees (HTML, CSS and a little JavaScript). | Web and deployment members (the idea only) |
| `requirements.txt` | List of libraries the website needs (flask, numpy, pillow). | Anyone |
| `requirements-local.txt` | The extra library the local program needs (matplotlib). | Anyone |
| `README.md` | Explanation shown on the GitHub page. | Anyone |

## 4. The matrix functions in `app.py`, explained function by function

### 4.1 The top of the file

```python
import base64
import io
import os
import sys

import numpy as np
from flask import Flask, jsonify, request, send_from_directory
from PIL import Image
```

We import the tools we need: `numpy` for matrices, `PIL` (the Pillow library) for opening and saving picture files, and `Flask` for the website. `base64` and `io` are only used to send images to the web page, and `os` and `sys` are used by the local program to create the output folder and read what you type after the program name.

### 4.2 `load_image`: read the image

```python
def load_image(file, max_side=1200):
    img = Image.open(file).convert("RGB")
    img.thumbnail((max_side, max_side))
    return np.asarray(img, dtype=np.uint8)
```

- `Image.open(file)` opens the picture from the computer.
- `.convert("RGB")` forces three colour channels, even if the original is a PNG with transparency or already gray.
- `thumbnail(...)` shrinks very large images so the longest side is at most 1200 pixels. This keeps the program fast.
- `np.asarray(...)` turns the picture into a NumPy array: the matrix. **This is the moment the picture becomes numbers.**

**Say to the professor:** "This function reads the image file and converts it into an H by W by 3 matrix of integers from 0 to 255."

### 4.3 `to_grayscale`: colour to gray

```python
def to_grayscale(rgb):
    weights = np.array([0.299, 0.587, 0.114])
    return np.rint(rgb.astype(np.float64) @ weights).astype(np.uint8)
```

Math: Gray = 0.299·R + 0.587·G + 0.114·B.

Line by line:

1. `weights` is the vector (0.299, 0.587, 0.114).
2. `rgb.astype(np.float64)` converts to decimals so nothing is rounded too early.
3. `@ weights` multiplies every pixel's (R, G, B) by the weights and adds: a dot product for every pixel. An H × W × 3 array times a 3-element vector gives an H × W matrix, which is the gray image.
4. `np.rint` rounds to whole numbers, and `.astype(np.uint8)` converts back to valid pixel values.

**Why unequal weights?** The human eye is most sensitive to green and least to blue, so green counts the most. The weights sum to 1, so the result never exceeds 255.

**Example:** pixel (200, 100, 50) gives 59.8 + 58.7 + 5.7 = 124.2, which rounds to 124.

### 4.4 `adjust_brightness`

```python
def adjust_brightness(img, beta):
    return np.clip(img.astype(np.int16) + int(beta), 0, 255).astype(np.uint8)
```

Math: I' = clip(I + β, 0, 255). Adding β to every entry is the same as adding β times a matrix of all ones.

1. `astype(np.int16)`: use bigger numbers so 240 + 50 does not wrap around to 34.
2. `+ int(beta)`: add β to every pixel. Positive β brightens, negative β darkens.
3. `np.clip(..., 0, 255)`: anything above 255 becomes 255, anything below 0 becomes 0.
4. `astype(np.uint8)`: back to pixel type.

**Example (β = 50):** 100 → 150. 240 → 290 → clipped to 255.

### 4.5 `flip_horizontal` and `flip_horizontal_matrix`

```python
def flip_horizontal(img):
    return img[:, ::-1]
```

This reverses the order of the columns: the mirror image.

The linear algebra version:

```python
def flip_horizontal_matrix(img):
    J = np.eye(img.shape[1])[::-1]
    if img.ndim == 3:
        out = np.einsum("hwc,wv->hvc", img.astype(np.float64), J)
    else:
        out = img @ J
    return np.rint(out).astype(np.uint8)
```

- `np.eye(n)` creates the n × n identity matrix.
- `[::-1]` reverses its rows, which turns it into J, the **exchange matrix** (ones on the anti-diagonal).
- Multiplying the image on the right by J reverses its columns: I' = I · J.
- `np.einsum(...)` is just a way to say "multiply every colour layer of the image by J". You can describe it as "matrix multiplication applied to each of the three colour matrices".

For a 3-column image, J is:

```
| 0 0 1 |
| 0 1 0 |
| 1 0 0 |
```

and \[10 20 30\] · J = \[30 20 10\].

**Why two versions?** The slicing version is faster and simpler; the J version shows the linear algebra. We tested that both give exactly the same image. Nice fact: J · J = I, so flipping twice gives back the original.

### 4.6 `to_black_white`

```python
def to_black_white(rgb, threshold=128):
    return np.where(to_grayscale(rgb) >= threshold, 255, 0).astype(np.uint8)
```

Math: B(i,j) = 255 if Gray(i,j) ≥ T, otherwise 0.

1. `to_grayscale(rgb)` first makes the gray matrix.
2. `>= threshold` makes a True/False matrix: is each pixel at least as bright as T?
3. `np.where(cond, 255, 0)`: where True put 255 (white), where False put 0 (black).

`threshold=128` is a default: if nobody provides T, it uses 128, the middle of 0–255. A smaller T gives more white; a larger T gives more black.

### 4.7 The helper functions

- `to_data_url`: converts a matrix back into a PNG picture, written as text that the web page can display. This is the reverse of `load_image`.
- `apply_operation(rgb, op, ...)`: a menu. It looks at the name of the operation ("grayscale", "brightness", "flip", "bw") and calls the matching function above.

## 5. `run_local`: the local program

Run it with:

```
python app.py path/to/image.jpg 50 128
```

The three things after `python app.py` are: the image path, the brightness value β (50) and the threshold T (128). If you type nothing after `python app.py`, it starts the website instead. What `run_local` does, in order:

1. The bottom of the file reads the path and the two numbers (`sys.argv` is the list of things typed after the program name) and passes them to `run_local`.
2. It calls `load_image` to get the matrix.
3. It builds a list called `results` of (name, matrix) pairs: the original and the four processed images.
4. It creates the `output` folder, draws all images in one row with Matplotlib (original and results side by side), and saves each image as a PNG plus a combined `comparison.png`.
5. `plt.show()` opens the window so you can see before and after.

This covers the project requirement: "display the images before and after processing and save the results".

## 6. The website, in plain words

You do not need to explain every line, only the idea.

- **The page** is the file `public/index.html` (written in HTML). It is what the user sees: a file picker, a dropdown for the operation, two sliders, and two image boxes. A bit of JavaScript sends the chosen image to the server whenever something changes.
- **The server part of `app.py`** (Flask) receives the image, calls `load_image` and `apply_operation`, and sends back the original and the result as pictures. The key line `@app.route("/api/process", methods=["POST"])` means "when the page sends something to the address /api/process, run the function below". A second small function, `home`, just hands over `index.html` when you run the site on your own computer (on Vercel the `public` folder is served automatically).
- Important point: the website uses **exactly the same matrix functions** as the local program, and they are in the same Python file. The web part is just a wrapper around them.

## 7. GitHub and Vercel in plain words

- **Git** records the history of your code. **GitHub** is a website that stores a copy of it online so the whole team can see and download it.
- **Vercel** is a hosting service. You connect it to the GitHub repository and it publishes the website at a public link. When you update the code on GitHub, Vercel republishes automatically.
- **How can one file work both ways?** The last lines of `app.py` check whether you typed an image path. If yes, the local program runs (it opens a window on your computer). If not, the website starts. On Vercel only the website part is used, because a website cannot open a window on your computer.

## 8. Questions the professor may ask (with answers)

**Q1. What is a digital image mathematically?** A matrix of numbers. For gray, one H × W matrix; for colour, three matrices (R, G, B), i.e. H × W × 3, with entries from 0 to 255.

**Q2. How did you read the image?** With Pillow's `Image.open`, then `np.asarray` converts it to a NumPy matrix.

**Q3. Why are the grayscale weights not equal (1/3 each)?** The eye is most sensitive to green, then red, and least sensitive to blue, so we use 0.299, 0.587 and 0.114. They sum to 1 so the result stays in 0–255.

**Q4. Which linear algebra operation is grayscale?** A dot product (matrix–vector product) of each pixel's colour vector with the weight vector.

**Q5. Why convert to `int16` or `float64` before calculating?** Pixels are stored as `uint8` (0–255). Adding or multiplying can leave that range and wrap around (240 + 50 would become 34). A bigger type keeps the true value; then we clip and convert back.

**Q6. What does `clip` do and why do we need it?** It forces values into 0–255. Without it, brighter-than-white or darker-than-black values are invalid and would wrap around and produce wrong colours.

**Q7. Which matrix operation is the brightness change?** Adding a constant to every entry: I + βE, with E the matrix of ones, followed by clipping.

**Q8. How is the horizontal flip a matrix operation?** Multiplication on the right by the exchange matrix J (ones on the anti-diagonal): I' = I · J. It reverses the column order.

**Q9. Is flipping twice the identity?** Yes, J · J = I, so (I · J) · J = I. Flipping twice returns the original image.

**Q10. What is the difference between multiplying by J on the left and on the right?** On the right (I · J) reverses the columns (horizontal flip). On the left (J · I) reverses the rows (vertical flip).

**Q11. How does black and white work and what is the threshold?** We make the gray matrix, then every pixel with value ≥ T becomes 255 and every other becomes 0. T = 128 is the middle of the range; changing T changes how much of the image turns white.

**Q12. Why convert to gray before black and white?** Thresholding needs one number per pixel; a colour pixel has three.

**Q13. Why NumPy and not ordinary loops?** NumPy applies an operation to all millions of entries at once, which is much faster and the code is much shorter and looks like the math.

**Q14. Is black and white the same as grayscale?** No. Gray has 256 levels (0–255); black and white has only two (0 and 255).

**Q15. What is the shape of the image matrix?** Colour: (height, width, 3). Gray or black and white: (height, width).

**Q16. How does this relate to artificial intelligence?** Computer-vision models receive images as matrices. Preprocessing such as grayscale conversion, brightness changes and flips is commonly applied before training or recognition; flipping is also used to create extra training images (data augmentation).

**Q17. How do you run the project?** `python app.py image.jpg 50 128` runs the local program. `python app.py` with nothing after it starts the website, or you can open the hosted website, upload an image and choose an operation.

**Q18. What are GitHub and Vercel used for here?** GitHub stores the code; Vercel publishes the web version directly from it.

## 9. Practice before the discussion

1. Everyone runs `python main.py` once on their own laptop with their own photo, and changes β and T to see the effect.
2. Each member picks one operation and practises explaining it in 1 minute: the formula, a small numeric example with pixel values, then the matching lines of code.
3. Swap parts and test each other with the questions in section 8.
4. Be ready to answer "what happens if...": β is negative; T is 0 (everything white) or 255 (almost everything black); the image is already gray.

## 10. Setup on a computer (if you want to run it)

1. Install Python from python.org (tick "Add Python to PATH" during installation).
2. Open a terminal in the project folder and run: `pip install numpy pillow matplotlib flask`
3. Run: `python app.py path/to/image.jpg 50 128`. To start the website instead, run `python app.py` and open http://127.0.0.1:5000

## 11. Mini glossary

| Term | Meaning |
| --- | --- |
| Pixel | One dot of the image; one entry of the matrix. |
| Channel | One colour layer (R, G or B). |
| Array | NumPy's name for a matrix. |
| Shape | The size of the array. |
| Clip | Force values into a range. |
| Threshold | A cut-off value: above it one result, below it another. |
| Exchange matrix | Matrix of ones on the anti-diagonal; reverses order when multiplied. |
| uint8 | Whole numbers from 0 to 255. |
| Library | A toolbox of ready-made functions (NumPy, Pillow). |
