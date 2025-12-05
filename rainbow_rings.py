import time
import re
import math
import numpy as np
from rpi_ws281x import PixelStrip, Color

# ----------------- SETTINGS -----------------
LED_PIN = 18
MAX_BRIGHTNESS = 100
UPDATE_DELAY = 0.05
ROTATION_SPEED = np.pi / 36
COLOR_SPEED = 0.02  # slower increment for smoother gradient

# ----------------- CYLINDRICAL COORDS -----------------
class cyl_coords:
    def __init__(self, coords, idx):
        self.r = math.sqrt(coords[0]**2 + coords[1]**2)
        self.theta = math.atan2(coords[1], coords[0])  # y,x
        self.z = coords[2]
        self.color = [0, 0, 0]  # GRB
        self.idx = idx

    def rotate(self, rotation):
        self.theta = (self.theta + rotation) % (2 * np.pi)

# ----------------- LOAD COORDINATES -----------------
def load_coords(filename):
    coords_raw = open(filename, 'r').readlines()
    coords_bits = [line.split(",") for line in coords_raw]
    coords = []
    for slab in coords_bits:
        new_coord = [int(re.sub(r'[^-\d]', '', val)) for val in slab]
        coords.append(new_coord)
    return coords

# ----------------- HSV TO GRB -----------------
def hsv_to_grb(h, s, v):
    """Convert HSV [0-1] to GRB [0-255]"""
    i = int(h * 6.0)
    f = (h * 6.0) - i
    p = int(v * (1.0 - s) * 255)
    q = int(v * (1.0 - f * s) * 255)
    t = int(v * (1.0 - (1.0 - f) * s) * 255)
    v = int(v * 255)
    i = i % 6
    if i == 0:
        return [q, v, p]
    if i == 1:
        return [p, v, t]
    if i == 2:
        return [p, q, v]
    if i == 3:
        return [t, p, v]
    if i == 4:
        return [v, p, q]
    if i == 5:
        return [v, t, p]

# ----------------- MAIN LIGHTS FUNCTION -----------------
def xmaslight():
    coords = load_coords("coords_brackets.txt")
    PIXEL_COUNT = len(coords)

    strip = PixelStrip(PIXEL_COUNT, LED_PIN, 800000, 10, False, MAX_BRIGHTNESS, 0, None)
    strip.begin()

    cyl_coords_set = [cyl_coords(c, i) for i, c in enumerate(coords)]
    max_z = max(c.z for c in cyl_coords_set)
    min_z = min(c.z for c in cyl_coords_set)

    inc = 0.0

    while True:
        for c in cyl_coords_set:
            # Map Z to 0-1 for gradient
            z_norm = (c.z - min_z) / (max_z - min_z)
            # Add incremental rotation for moving rainbow
            h = (z_norm + inc) % 1.0
            c.color = hsv_to_grb(h, 1.0, 1.0)  # Full saturation and brightness
            c.rotate(ROTATION_SPEED)
            strip.setPixelColor(c.idx, Color(int(c.color[1]), int(c.color[0]), int(c.color[2])))

        strip.show()
        inc = (inc + COLOR_SPEED) % 1.0
        time.sleep(UPDATE_DELAY)

if __name__ == "__main__":
    xmaslight()
