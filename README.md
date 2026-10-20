# Pure-Python Image Processor

A lightweight, **terminal-based image processing application** built entirely with Python's standard features—no external packages required. It lets you load or create images, apply image-processing operations, preview the results in your terminal, undo changes, and save the finished image.

The project is designed around simple 2D lists of pixel values, making it useful for learning how basic image-processing algorithms work without relying on libraries such as Pillow, OpenCV, or NumPy.

## Features

- **11 image-processing operations**, including inversion, brightness adjustment, thresholding, flips, rotations, cropping, blur, and edge detection.
- **Grayscale and RGB support**, with automatic per-channel processing for operations such as inversion, brightness adjustment, and blur.
- **Interactive command-line menu** for choosing operations and adjusting parameters.
- **Built-in sample images** and an option to enter a small grayscale image manually.
- **Before-and-after previews** with pixel values for small images and ASCII-art previews for larger ones.
- **Undo and reset** capabilities, plus the ability to chain multiple operations.
- **PGM/PPM file loading and saving** without third-party dependencies.

## Requirements

- Python 3
- A terminal or command prompt

No installation of additional Python packages is necessary.

## Project Structure

```text
.
├── main.py       # Interactive CLI, input handling, menu, and operation history
├── imgproc.py    # Image processing, previews, validation, and PNM file I/O
└── README.md     # Project documentation
```

## Getting Started

1. Place `main.py` and `imgproc.py` in the same directory.
2. Open a terminal in that directory.
3. Run:

   ```bash
   python main.py
   ```

   On systems where Python 3 is launched using `python3`, run `python3 main.py` instead.

4. Select how to provide an image:

   | Option | Input method |
   | --- | --- |
   | `1` | Load a `.pgm` (grayscale) or `.ppm` (RGB) file |
   | `2` | Enter grayscale pixel values manually |
   | `3` | Use the built-in 5 × 5 gradient |
   | `4` | Use the built-in 5 × 5 sharp-edge sample |
   | `5` | Use the built-in 3 × 2 RGB sample |

5. Choose operations from the menu. After each successful operation, the program displays the original and updated images and adds the result to the undo history.

## Available Operations

| Key | Operation | Description |
| --- | --- | --- |
| `1` | Invert | Replaces each intensity value with `255 - value`. |
| `2` | Brightness | Adds a chosen amount from `-255` to `255`, clipping values to the valid range. |
| `3` | Threshold | Converts pixels to black (`0`) or white (`255`) using a chosen threshold. |
| `4` | Flip horizontal | Mirrors the image left to right. |
| `5` | Flip vertical | Mirrors the image top to bottom. |
| `6` | Rotate clockwise | Rotates the image 90° clockwise. |
| `7` | Rotate counter-clockwise | Rotates the image 90° counter-clockwise. |
| `8` | Crop | Extracts a rectangular region from the image. |
| `9` | Box blur | Applies a 3 × 3 averaging filter. |
| `10` | Edge detection | Applies a Laplacian kernel to highlight changes in intensity. |
| `11` | Grayscale | Converts RGB pixels to grayscale using weighted red, green, and blue values. |

**Color behavior:** Inversion, brightness adjustment, and box blur work independently on each RGB channel. Thresholding and edge detection first convert an RGB image to grayscale, so their results are grayscale. Grayscale conversion is only applicable to RGB images.

### Other Menu Commands

| Key | Action |
| --- | --- |
| `v` | View the current image |
| `u` | Undo the previous operation |
| `r` | Reset to the initial image |
| `s` | Save the current image to a file |
| `l` | Load or create a different image |
| `m` | Display the menu again |
| `q` | Quit |

## Example Walkthrough

Start the application:

```bash
python main.py
```

Then:

1. Enter `4` at the image-selection prompt to load the built-in sharp-edge image.
2. Enter `9` to apply a **3 × 3 box blur** and see the before-and-after previews.
3. Enter `10` to apply **edge detection** to the blurred result.
4. Enter `u` to undo the edge-detection step, or `r` to restore the starting image.
5. Enter `s` and supply a filename such as `output.pgm` to save the current result.
6. Enter `q` to exit.

### Entering an Image Manually

Choose input option `2`, then enter one row per line, for example:

```text
0 0 255
0 128 255
255 255 255
```

Press Enter on an empty line to finish. Each value must be between `0` and `255`, and every row must have the same number of values.

## Supported Image Formats

The reader supports these **8-bit PNM formats**:

| Format | File type | Encoding |
| --- | --- | --- |
| `P2` | PGM grayscale | Plain-text ASCII |
| `P3` | PPM RGB | Plain-text ASCII |
| `P5` | PGM grayscale | Binary |
| `P6` | PPM RGB | Binary |

The program accepts PNM files with a maximum pixel value of **1–255** and scales lower maximum values internally to the 0–255 range.

**Saving:** Grayscale images are written as ASCII `P2` `.pgm` files; color images are written as ASCII `P3` `.ppm` files. The appropriate extension is appended automatically if it is missing. Existing files with the same name may be overwritten.

**Note:** PNG, JPEG, GIF, and other common image formats are not supported directly. Convert them to PGM or PPM first using another image tool if needed.

## How Images Are Represented

Grayscale images are 2D lists containing intensity values between 0 (black) and 255 (white):

```python
gray = [
    [0, 128, 255],
    [30, 160, 220],
]
```

RGB images use `(red, green, blue)` tuples for each pixel:

```python
color = [
    [(255, 0, 0), (0, 255, 0)],
    [(0, 0, 255), (255, 255, 255)],
]
```

For small images, the application prints the pixel numbers. Larger images are rendered as approximate ASCII-art previews, using darker characters for darker pixels and lighter characters for brighter ones.

## Using `imgproc.py` Directly

The image-processing functions can also be imported into your own Python code:

```python
from imgproc import invert, adjust_brightness, box_blur, save_image

image = [
    [0, 100, 200],
    [50, 150, 255],
    [25, 125, 225],
]

inverted = invert(image)
brighter = adjust_brightness(inverted, 20)
blurred = box_blur(brighter)

save_image("result.pgm", blurred)
```

Functions such as `invert`, `adjust_brightness`, `threshold`, `box_blur`, and `edge_detect` operate on grayscale arrays. To use grayscale-only operations on RGB images programmatically, use `apply_per_channel` when appropriate, or convert the image using `to_grayscale`.

## Implementation Notes and Limitations

- Processing is performed using nested Python lists and loops rather than optimized imaging libraries, so large images can be slow, especially with neighborhood filters.
- Convolution-based operations use **replicated border pixels** to handle image edges.
- Computed pixel values are rounded and clamped to the range 0–255.
- Cropping uses **zero-based** row and column positions.
- Undo tracks the history of processed images in memory; loading a new image starts a new history.
- The application is a text-based processor, not a graphical image editor, and its previews are approximate representations of the pixel data.

## Files

- **`main.py`** — starts the application and implements its interactive workflow.
- **`imgproc.py`** — contains the reusable image-processing and PGM/PPM input/output functions.

## Educational Purpose

This project demonstrates fundamental image-processing concepts including per-pixel transformations, geometric transformations, convolution kernels, RGB channel manipulation, and basic image file formats using readable, dependency-free Python code.
