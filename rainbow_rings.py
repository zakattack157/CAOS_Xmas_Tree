import time
import re
import math
import numpy as np
from rpi_ws281x import PixelStrip, Color

# ----------------- SETTINGS -----------------
LED_PIN = 18
MAX_BRIGHTNESS = 100        # Max brightness of LEDs
UPDATE_DELAY = 0.05         # Seconds per frame (adjust speed)
ROTATION_SPEED = np.pi / 36 # radians per frame, slower rotation
COLOR_SPEED = 0.05           # increment for smooth color cycling

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

# ----------------- MAIN LIGHTS FUNCTION -----------------
def xmaslight():
    coords = load_coords("coords_brackets.txt")
    PIXEL_COUNT = len(coords)

    # Initialize LED strip
    strip = PixelStrip(PIXEL_COUNT, LED_PIN, 800000, 10, False, MAX_BRIGHTNESS, 0, None)
    strip.begin()

    # Convert to cylindrical coordinates
    cyl_coords_set = [cyl_coords(c, i) for i, c in enumerate(coords)]
    max_z = max(c.z for c in cyl_coords_set)
    min_z = min(c.z for c in cyl_coords_set)

    # GRB Color palette
    colors = np.array([
        [0, 30, 0], [15, 15, 0], [30, 0, 0],
        [0, 15, 15], [0, 0, 30], [15, 0, 15]
    ])
    ring_height = (max_z - min_z) / (len(colors) - 1)
    inc = 0.0

    while True:
        # Update LED colors
        for c in cyl_coords_set:
            z_bin = int(round((c.z - min_z) / ring_height + inc)) % len(colors)
            c.rotate(ROTATION_SPEED)
            adjusted_rotation = (c.theta + np.pi / 6.0 * z_bin) % (2.0 * np.pi)
            intensity = adjusted_rotation / np.pi  # Scale 0–2
            c.color = np.clip(np.rint(colors[z_bin] * intensity), 0, 255)

        # Write to LED strip (GRB)
        for c in cyl_coords_set:
            strip.setPixelColor(c.idx, Color(int(c.color[1]), int(c.color[0]), int(c.color[2])))
        strip.show()

        # Increment color ring gradually for smooth transitions
        inc = (inc + COLOR_SPEED) % len(colors)
        time.sleep(UPDATE_DELAY)

# ----------------- AUTO RUN -----------------
if __name__ == "__main__":
    xmaslight()
