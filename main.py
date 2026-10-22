
from imgproc import *


#reading input

def ask(prompt):
    try:
        return input(prompt).strip()
    except EOFError:
        print("\nInput ended, goodbye.")
        raise SystemExit


def ask_int(prompt, low, high, default=None):
    while True:
        text = ask(prompt)
        if text == "" and default is not None:
            return default
        try:
            value = int(text)
        except ValueError:
            print("  Please type a whole number.")
            continue
        if value < low or value > high:
            print(f"  Please type a number from {low} to {high}.")
            continue
        return value


#Getting image

def load_from_file():
    path = ask("  Path to a .pgm or .ppm file: ").strip("\"'")
    if path == "":
        return None
    try:
        return read_pnm(path)
    except (OSError, ValueError) as error:
        print(f"  Could not load that file: {error}")
        return None


def type_by_hand():
    print("  Type one row per line, values from 0 to 255 separated by spaces.")
    print("  Press Enter on an empty line when you are done.")
    rows = []
    while True:
        line = ask(f"  row {len(rows) + 1}: ")
        if line == "":
            break
        try:
            row = [int(token) for token in line.split()]
        except ValueError:
            print("   Numbers only, please.")
            continue
        if any(v < 0 or v > 255 for v in row):
            print("   Every value must be between 0 and 255.")
            continue
        if rows and len(row) != len(rows[0]):
            print(f"   Every row needs {len(rows[0])} values (like the first row).")
            continue
        rows.append(row)
    if not rows:
        print("  No rows entered.")
        return None
    return rows


def choose_image():
    while True:
        print()
        print("=== CHOOSE AN IMAGE ===")
        print(" 1) Load a file (.pgm gray or .ppm colour)")
        print(" 2) Type a small grayscale image by hand")
        print(" 3) Built-in sample: 5x5 gradient")
        print(" 4) Built-in sample: 5x5 sharp edge (good for blur / edge detection)")
        print(" 5) Built-in sample: 3x2 colour image")
        choice = ask("Choose 1-5: ")
        img = None
        if choice == "1":
            img = load_from_file()
        elif choice == "2":
            img = type_by_hand()
        elif choice == "3":
            img = [[10 + 50 * r + 10 * c for c in range(5)] for r in range(5)]
        elif choice == "4":
            img = [[0, 0, 0, 255, 255] for _ in range(5)]
        elif choice == "5":
            img = [[(255, 0, 0), (0, 255, 0), (0, 0, 255)],
                   [(255, 255, 0), (0, 255, 255), (128, 128, 128)]]
        else:
            print("  Please type a number from 1 to 5.")
            continue
        if img is not None:
            validate(img)
            return img


#OPERATIONS

def op_invert(img):
    return apply_per_channel(invert, img)


def op_brightness(img):
    delta = ask_int("  Amount to add (-255 to 255, negative = darker) [40]: ", -255, 255, 40)
    return apply_per_channel(adjust_brightness, img, delta)


def op_threshold(img):
    t = ask_int("  Threshold (0 to 255) [128]: ", 0, 255, 128)
    if is_color(img):
        print("  (colour image: converted to grayscale first, then thresholded)")
        img = to_grayscale(img)
    return threshold(img, t)


def op_flip_horizontal(img):
    return flip_horizontal(img)


def op_flip_vertical(img):
    return flip_vertical(img)


def op_rotate_cw(img):
    return rotate_90_cw(img)


def op_rotate_ccw(img):
    return rotate_90_ccw(img)


def op_crop(img):
    h, w = height(img), width(img)
    print(f"  The image is {w} wide and {h} tall. Rows are counted from 0 at the")
    print("  top, columns from 0 at the left.")
    top = ask_int(f"  Top row (0 to {h - 1}): ", 0, h - 1)
    left = ask_int(f"  Left column (0 to {w - 1}): ", 0, w - 1)
    crop_h = ask_int(f"  Height of the window (1 to {h - top}): ", 1, h - top)
    crop_w = ask_int(f"  Width of the window (1 to {w - left}): ", 1, w - left)
    return crop(img, top, left, crop_h, crop_w)


def op_box_blur(img):
    if height(img) * width(img) > 250000:
        print("  (big image, this can take a few seconds in plain Python...)")
    return apply_per_channel(box_blur, img)


def op_edge_detect(img):
    if is_color(img):
        print("  (colour image: converted to grayscale first, then edges found)")
        img = to_grayscale(img)
    if height(img) * width(img) > 250000:
        print("  (big image, this can take a few seconds in plain Python...)")
    return edge_detect(img)


def op_grayscale(img):
    if not is_color(img):
        print("  The image is already grayscale.")
        return None
    return to_grayscale(img)


MENU = [
    ("PIXEL-WISE   (each pixel changed on its own)", [
        ("1", "Invert", op_invert),
        ("2", "Brightness", op_brightness),
        ("3", "Threshold (black / white)", op_threshold),
    ]),
    ("GEOMETRIC    (pixels move, values stay)", [
        ("4", "Flip horizontal", op_flip_horizontal),
        ("5", "Flip vertical", op_flip_vertical),
        ("6", "Rotate 90 degrees clockwise", op_rotate_cw),
        ("7", "Rotate 90 degrees counter-clockwise", op_rotate_ccw),
        ("8", "Crop", op_crop),
    ]),
    ("NEIGHBOURHOOD (pixel + its neighbours, replicate borders)", [
        ("9", "Box blur 3x3", op_box_blur),
        ("10", "Edge detect (Laplacian)", op_edge_detect),
    ]),
    ("COLOUR", [
        ("11", "Convert to grayscale", op_grayscale),
    ]),
]

OPERATIONS = {key: (name, func) for _, items in MENU for key, name, func in items}


def print_menu(img, steps):
    print()
    print(f"=== MENU   current image: {describe(img)}   operations applied: {steps} ===")
    for heading, items in MENU:
        print(f" {heading}")
        for key, name, _ in items:
            print(f"   {key:>2}) {name}")
    print(" OTHER")
    print("    v) View current image    u) Undo    r) Reset to the starting image")
    print("    s) Save to a file        l) Load a different image    m) Show this menu")
    print("    q) Quit")


#Main loop

def save_current(img):
    path = ask("  File name to save as: ").strip("\"'")
    if path == "":
        print("  Not saved.")
        return
    extension = ".ppm" if is_color(img) else ".pgm"
    if not path.lower().endswith(extension):
        path += extension
    try:
        save_image(path, img)
        print(f"  Saved to {path}")
    except OSError as error:
        print(f"  Could not save: {error}")


def main():
    print("Pure-Python image processor")
    start = choose_image()
    history = [start]
    show_image("Starting image", start)


    show_menu = True
    while True:
        current = history[-1]
        if show_menu:
            print_menu(current, len(history) - 1)
            show_menu = False
        choice = ask(f"[{describe(current)}, {len(history) - 1} ops] "
                     "Choose an operation (m = show menu): ").lower()

        if choice in OPERATIONS:
            name, func = OPERATIONS[choice]
            print(f"--- {name} ---")
            result = func(current)
            if result is None:
                continue
            show_image("BEFORE", current)
            show_image(f"AFTER ({name})", result)
            history.append(result)
        elif choice == "v":
            show_image("Current image", current)
        elif choice == "u":
            if len(history) > 1:
                history.pop()
                show_image("Undone. Current image", history[-1])
            else:
                print("  Nothing to undo.")
        elif choice == "r":
            history.append(history[0])
            show_image("Reset to the starting image", history[-1])
        elif choice == "s":
            save_current(current)
        elif choice == "l":
            history = [choose_image()]
            show_image("Starting image", history[0])
        elif choice == "m":
            show_menu = True
        elif choice == "q":
            print("Goodbye.")
            break
        else:
            print("  Not a menu choice. Type a number from the list, or v, u, r, s, l, q, m.")
            show_menu = True


if __name__ == "__main__":
    main()
