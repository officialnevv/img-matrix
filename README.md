# Image Processing Using Matrices

**Linear Algebra Project Report**

Faculty / University: [fill in]  
Course: Linear Algebra  
Group number: [fill in]  
Supervising professor: [Dr. Eman El-Hadidy / Dr. Mohamed Khaled / Dr. Sherif El-Zeiny]  
Submission date: [fill in]

**Team members**

| # | Name | Student ID | Part presented |
|---|------|------------|----------------|
| 1 | [name] | [ID] | [e.g. Introduction and idea] |
| 2 | [name] | [ID] | [e.g. Grayscale] |
| 3 | [name] | [ID] | [e.g. Brightness] |
| 4 | [name] | [ID] | [e.g. Horizontal flip] |
| 5 | [name] | [ID] | [e.g. Black and white] |
| 6 | [name] | [ID] | [e.g. Web app and deployment] |

## 1. Introduction and Project Idea

Every digital image is, mathematically, a matrix of numbers. A grayscale image is one matrix in which each entry is the brightness of one pixel. A colour image is three matrices of the same size, one for red, one for green and one for blue. Because images are matrices, the operations we apply to them (making them gray, brighter, mirrored or black and white) are matrix operations.

This project is a program that lets the user choose a real image from their computer, apply these operations using matrices, view the original next to the processed image, and save the result. We also built a web version, hosted online, so the program can be used from any browser.

## 2. Objectives

- Apply the matrix concepts studied in the course to a real problem.
- Understand one application of matrices in image processing and artificial intelligence.
- Implement the required operations: reading an image, grayscale, brightness adjustment, horizontal flip, black and white, displaying before and after, and saving the results.
- Practise teamwork and be able to explain the maths and the code.

## 3. Mathematical Background

### 3.1 An image as a matrix

A grayscale image of height H and width W is a matrix A of size H × W. The entry A(i, j) is the intensity of the pixel in row i and column j, an integer from 0 (black) to 255 (white).

A colour image is a three-dimensional array of size H × W × 3, which is three H × W matrices R, G and B. Each pixel is the triple (R(i,j), G(i,j), B(i,j)).

Example, a 3 × 3 grayscale image:

```
| 10  20  30 |
| 40  50  60 |
| 70  80  90 |
```

### 3.2 Grayscale conversion

To convert a colour pixel to gray we take a weighted sum of its three channels:

```
Gray(i,j) = 0.299 · R(i,j) + 0.587 · G(i,j) + 0.114 · B(i,j)
```

This is the dot product of the pixel vector (R, G, B) with the weight vector w = (0.299, 0.587, 0.114). Applied to the whole image, it is a matrix–vector product: the H × W × 3 array multiplied by the vector w gives an H × W matrix. The weights are not equal because the human eye is most sensitive to green and least sensitive to blue. The weights add up to 1, so the result stays within 0–255.

Worked example. Pixel (R, G, B) = (200, 100, 50):

```
Gray = 0.299·200 + 0.587·100 + 0.114·50
     = 59.8 + 58.7 + 5.7 = 124.2  ->  124 (rounded)
```

### 3.3 Brightness adjustment

Brightness is changed by adding a constant β to every entry:

```
I'(i,j) = clip( I(i,j) + β , 0 , 255 )
```

In matrix form, I' = I + β·E, where E is the matrix of all ones. β > 0 brightens the image and β < 0 darkens it. The clip function keeps values inside the valid range: values above 255 become 255 and values below 0 become 0.

Worked example with β = 50: a pixel of 100 becomes 150. A pixel of 240 would be 290, which is clipped to 255.

### 3.4 Horizontal flip

A horizontal flip reverses the order of the columns of the image. In linear algebra this is multiplication by the exchange matrix J, which has ones on the anti-diagonal and zeros elsewhere:

```
I' = I · J

For W = 3:      | 0 0 1 |
            J = | 0 1 0 |
                | 1 0 0 |
```

Multiplying on the right by J reverses the columns. Example, one row [10 20 30]:

```
[10 20 30] · J = [30 20 10]
```

J has the nice property J · J = I (the identity), so flipping twice returns the original image. In the code we also use the equivalent shortcut of reading the columns in reverse order, and a test confirms both methods give identical results.

### 3.5 Black and white (thresholding)

First the image is converted to gray, then each pixel is compared with a threshold T (default 128):

```
B(i,j) = 255   if Gray(i,j) >= T
         0     otherwise
```

The result contains only two values, 0 (black) and 255 (white). Example with T = 128: a gray pixel of 124 becomes 0, and a gray pixel of 130 becomes 255.

## 4. Tools Used

| Tool | Purpose |
|------|---------|
| Python 3 | Programming language |
| NumPy | Fast matrix (array) operations |
| Pillow (PIL) | Reading and saving image files |
| Matplotlib | Displaying before and after images in the local program |
| Flask | Small web server for the online version |
| GitHub | Storing and sharing the source code |
| Vercel | Hosting the web version online |

## 5. Implementation

The project has one Python file, `app.py`, and one web page file, `public/index.html`. `app.py` has three parts: the matrix functions (`load_image`, `to_grayscale`, `adjust_brightness`, `flip_horizontal`, `to_black_white` and the helpers around them), the local program (`run_local`, which runs when an image path is given on the command line) and the web server (Flask). The page the user sees is `public/index.html`.

### 5.1 Reading the image

The image is opened with Pillow, converted to RGB, and turned into a NumPy array of integers from 0 to 255. Very large images are shrunk so that the longest side is at most 1200 pixels.

```python
def load_image(file, max_side=1200):
    img = Image.open(file).convert("RGB")
    img.thumbnail((max_side, max_side))
    return np.asarray(img, dtype=np.uint8)
```

### 5.2 Grayscale

```python
def to_grayscale(rgb):
    weights = np.array([0.299, 0.587, 0.114])
    return np.rint(rgb.astype(np.float64) @ weights).astype(np.uint8)
```

The operator `@` is matrix multiplication. The array is converted to decimals first so the weighted sum is not rounded too early.

### 5.3 Brightness

```python
def adjust_brightness(img, beta):
    return np.clip(img.astype(np.int16) + int(beta), 0, 255).astype(np.uint8)
```

The values are converted to a larger integer type before adding, because 8-bit numbers would wrap around (240 + 50 would become 34 instead of 290).

### 5.4 Horizontal flip

```python
def flip_horizontal(img):
    return img[:, ::-1]


def flip_horizontal_matrix(img):
    J = np.eye(img.shape[1])[::-1]
    if img.ndim == 3:
        out = np.einsum("hwc,wv->hvc", img.astype(np.float64), J)
    else:
        out = img @ J
    return np.rint(out).astype(np.uint8)
```

The first function reverses the columns directly. The second builds the exchange matrix J and multiplies by it, exactly as in section 3.4.

### 5.5 Black and white

```python
def to_black_white(rgb, threshold=128):
    return np.where(to_grayscale(rgb) >= threshold, 255, 0).astype(np.uint8)
```

### 5.6 Displaying and saving

The function `run_local` in `app.py` applies all operations, shows the original and every result side by side with Matplotlib, and saves each result as a PNG file in the `output` folder, together with a comparison picture.

```
python app.py path/to/image.jpg 50 128
```

The two numbers are the brightness value β and the black and white threshold T.

### 5.7 Web version

The web page (`public/index.html`) lets the user upload an image, choose an operation, adjust the brightness or threshold with sliders, and see the original and processed image next to each other with a button to save the result. The page sends the image to a Flask server in `app.py`, which applies the same matrix functions and returns both images. Running `python app.py` with no arguments starts this website on the local computer.

## 6. Results

Input image: [name of the image used, its size in pixels]

| Operation | Settings | Result |
|-----------|----------|--------|
| Original | none | [insert screenshot] |
| Grayscale | none | [insert screenshot] |
| Brightness increased | β = +50 | [insert screenshot] |
| Brightness decreased | β = -50 | [insert screenshot] |
| Horizontal flip | none | [insert screenshot] |
| Black and white | T = 128 | [insert screenshot] |
| Black and white | T = [another value] | [insert screenshot] |

Observations: [write 3–4 sentences, for example: increasing β made bright areas saturate at 255 and lose detail; a lower threshold T produced more white pixels; the flipped image is a mirror image and flipping twice returns the original.]

## 7. Hosting and Source Code

- GitHub repository: [link]
- Live website (Vercel): [link]

The code is stored on GitHub and the web version is deployed on Vercel directly from the repository, so every update to the code can be published automatically.

## 8. Conclusion

The project showed that common image operations are simple matrix operations: a weighted sum for grayscale, adding a constant matrix for brightness, multiplying by the exchange matrix for flipping, and comparing every entry with a number for thresholding. Using NumPy made it possible to apply these operations to millions of pixels at once. The same idea of treating images as matrices is the basis of more advanced image processing and of the computer vision used in artificial intelligence.

## 9. Team Contributions

| Member | Contribution |
|--------|--------------|
| [name] | [what they did] |
| [name] | [what they did] |
| [name] | [what they did] |
| [name] | [what they did] |
| [name] | [what they did] |
| [name] | [what they did] |

## 10. References

- Lecture notes of the Linear Algebra course.
- NumPy documentation: https://numpy.org/doc/
- Pillow documentation: https://pillow.readthedocs.io/
- Flask documentation: https://flask.palletsprojects.com/

## 11. How to Run the Project

```
pip install -r requirements.txt -r requirements-local.txt
python app.py path/to/image.jpg 50 128    # local program
python app.py                             # website at http://127.0.0.1:5000
```

The team guides are in the `docs/` folder.
