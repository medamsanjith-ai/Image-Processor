#Functions

def height(img):
    return len(img)


def width(img):
    return len(img[0])


def clamp(v):
    return max(0, min(255, int(round(v))))


def is_color(img):
    return isinstance(img[0][0], tuple)


def validate(img):
    if not img or not img[0]:
        raise ValueError("image is empty")
    w = len(img[0])
    for row in img:
        if len(row) != w:
            raise ValueError("rows have different lengths")
        for px in row:
            if isinstance(px, tuple):
                if len(px) != 3:
                    raise ValueError("colour pixels need exactly 3 values")
                values = px
            else:
                values = (px,)
            for v in values:
                if not 0 <= v <= 255:
                    raise ValueError(f"pixel value {v} outside 0..255")


def show(title, img):
    print(title)
    for row in img:
        print("  " + " ".join(f"{v:3d}" for v in row))
    print()


def show_rgb(title, img):
    print(title)
    for row in img:
        print("  " + " ".join(f"({r:3d},{g:3d},{b:3d})" for r, g, b in row))
    print()


def describe(img):
    kind = "RGB" if is_color(img) else "grayscale"
    return f"{width(img)}x{height(img)} {kind}"


RAMP = " .:-=+*#%@"


def _brightness(px):
    if isinstance(px, tuple):
        return 0.299 * px[0] + 0.587 * px[1] + 0.114 * px[2]
    return px


def ascii_preview(img, max_cols=78):
    h, w = height(img), width(img)
    if w * 2 <= max_cols:
        block_w, block_h, repeat = 1, 1, 2
    else:
        block_w = (w + max_cols - 1) // max_cols
        block_h = block_w * 2
        repeat = 1
    lines = []
    for y0 in range(0, h, block_h):
        line = ""
        for x0 in range(0, w, block_w):
            total = 0
            count = 0
            for y in range(y0, min(y0 + block_h, h)):
                for x in range(x0, min(x0 + block_w, w)):
                    total += _brightness(img[y][x])
                    count += 1
            avg = total / count
            index = min(len(RAMP) - 1, int(avg * len(RAMP) / 256))
            line += RAMP[index] * repeat
        lines.append(line)
    return lines


def show_image(title, img):
    label = f"{title}  [{describe(img)}]"
    limit = 6 if is_color(img) else 12
    if height(img) <= 12 and width(img) <= limit:
        (show_rgb if is_color(img) else show)(label, img)
    else:
        print(label)
        print("  (too big to print every number; text preview, ' ' = black, '@' = white)")
        for line in ascii_preview(img):
            print("  " + line)
        print()


#Pixel wise operations

def invert(img):
    return [[255 - v for v in row] for row in img]


def adjust_brightness(img, delta):
    return [[clamp(v + delta) for v in row] for row in img]


def threshold(img, t):
    return [[255 if v >= t else 0 for v in row] for row in img]


#Geometric operations

def flip_horizontal(img):
    return [row[::-1] for row in img]


def flip_vertical(img):
    return [row[:] for row in reversed(img)]


def rotate_90_cw(img):
    h, w = height(img), width(img)
    return [[img[h - 1 - c][r] for c in range(h)] for r in range(w)]


def rotate_90_ccw(img):
    h, w = height(img), width(img)
    return [[img[c][w - 1 - r] for c in range(h)] for r in range(w)]


def crop(img, top, left, h, w):
    if top < 0 or left < 0 or top + h > height(img) or left + w > width(img):
        raise ValueError("crop window falls outside the image")
    return [row[left:left + w] for row in img[top:top + h]]


#Neighbourhood operations

def convolve(img, kernel, divisor=1):
    h, w = height(img), width(img)
    k = len(kernel)
    half = k // 2
    out = []
    for r in range(h):
        new_row = []
        for c in range(w):
            acc = 0
            for ky in range(k):
                for kx in range(k):
                    y = min(max(r + ky - half, 0), h - 1)
                    x = min(max(c + kx - half, 0), w - 1)
                    acc += img[y][x] * kernel[ky][kx]
            new_row.append(clamp(acc / divisor))
        out.append(new_row)
    return out


def box_blur(img):
    return convolve(img, [[1, 1, 1], [1, 1, 1], [1, 1, 1]], divisor=9)


def edge_detect(img):
    return convolve(img, [[0, -1, 0], [-1, 4, -1], [0, -1, 0]])


#Colour operations

def split_channels(img):
    return [[[px[i] for px in row] for row in img] for i in range(3)]


def merge_channels(red, green, blue):
    return [[(red[y][x], green[y][x], blue[y][x]) for x in range(width(red))]
            for y in range(height(red))]


def apply_per_channel(func, img, *args):
    if not is_color(img):
        return func(img, *args)
    red, green, blue = [func(ch, *args) for ch in split_channels(img)]
    return merge_channels(red, green, blue)


def invert_rgb(img):
    return [[(255 - r, 255 - g, 255 - b) for r, g, b in row] for row in img]


def to_grayscale(img):
    return [[clamp(0.299 * r + 0.587 * g + 0.114 * b) for r, g, b in row]
            for row in img]


#Read/Write image files

_WHITESPACE = b" \t\n\r\x0b\x0c"


def read_pnm(path):
    with open(path, "rb") as f:
        data = f.read()
    n = len(data)
    pos = 0

    def next_token():
        nonlocal pos
        while pos < n:
            ch = data[pos]
            if ch == 35:
                while pos < n and data[pos] != 10 and data[pos] != 13:
                    pos += 1
            elif ch in _WHITESPACE:
                pos += 1
            else:
                break
        start = pos
        while pos < n and data[pos] not in _WHITESPACE:
            pos += 1
        return data[start:pos].decode("ascii", "replace")

    magic = next_token()
    if magic not in ("P2", "P3", "P5", "P6"):
        raise ValueError("unsupported file type (need a PGM/PPM file: P2, P3, P5 or P6)")
    try:
        w, h, maxval = int(next_token()), int(next_token()), int(next_token())
    except ValueError:
        raise ValueError("the file header is not valid")
    if w <= 0 or h <= 0:
        raise ValueError("image size must be positive")
    if not 0 < maxval < 256:
        raise ValueError("only 8-bit images are supported (maxval up to 255)")

    channels = 3 if magic in ("P3", "P6") else 1
    count = w * h * channels

    if magic in ("P2", "P3"):
        values = []
        for _ in range(count):
            token = next_token()
            if token == "":
                raise ValueError("the file ends before all pixels are given")
            try:
                values.append(int(token))
            except ValueError:
                raise ValueError(f"expected a pixel number but found '{token}'")
    else:
        pos += 1
        raw = data[pos:pos + count]
        if len(raw) < count:
            raise ValueError("the file ends before all pixels are given")
        values = list(raw)

    for v in values:
        if v > maxval:
            raise ValueError(f"pixel value {v} is larger than maxval {maxval}")
    if maxval != 255:
        values = [v * 255 // maxval for v in values] 

    img = []
    i = 0
    for _ in range(h):
        row = []
        for _ in range(w):
            if channels == 3:
                row.append((values[i], values[i + 1], values[i + 2]))
            else:
                row.append(values[i])
            i += channels
        img.append(row)
    return img


read_ppm = read_pnm


def write_pgm(path, img):
    with open(path, "w") as f:
        f.write(f"P2\n{width(img)} {height(img)}\n255\n")
        for row in img:
            f.write(" ".join(str(v) for v in row) + "\n")


def write_ppm(path, img):
    with open(path, "w") as f:
        f.write(f"P3\n{width(img)} {height(img)}\n255\n")
        for row in img:
            f.write(" ".join(f"{r} {g} {b}" for r, g, b in row) + "\n")


def save_image(path, img):
    if is_color(img):
        write_ppm(path, img)
    else:
        write_pgm(path, img)
