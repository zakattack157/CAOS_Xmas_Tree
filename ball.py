import time
import re
import math
import numpy as np
from rpi_ws281x import PixelStrip, Color

# ----------------- SETTINGS -----------------
LED_PIN = 18
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_INVERT = False
LED_CHANNEL = 0
MAX_BRIGHTNESS = 100
FRAME_DELAY = 0.05  # seconds per frame
BOUNCE_SPEED = 0.1  # speed of bouncing

BALL_COLOR = [0, 255, 0]
BACKGROUND_COLOR = [255, 255, 255]

BALL_THICKNESS = 10  # z-distance for "ball size"

# ----------------- CYLINDRICAL COORDS -----------------
class cyl_coords:
    def __init__(self, coords, idx):
        self.x = coords[0]
        self.y = coords[1]
        self.z = coords[2]
        self.idx = idx
        self.color = BACKGROUND_COLOR.copy()  # default background

# ----------------- LOAD COORDINATES -----------------
def load_coords(filename):
    coords_raw = open(filename, 'r').readlines()
    coords_bits = [line.split(",") for line in coords_raw]
    coords = []
    for slab in coords_bits:
        new_coord = [int(re.sub(r'[^-\d]', '', val)) for val in slab]
        coords.append(new_coord)
    return coords

# ----------------- MAIN FUNCTION -----------------
def bouncing_ball():
    coords = load_coords("coords_brackets.txt")
    PIXEL_COUNT = len(coords)
    strip = PixelStrip(PIXEL_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT,
                       MAX_BRIGHTNESS, LED_CHANNEL)
    strip.begin()

    cyl_coords_set = [cyl_coords(c, i) for i, c in enumerate(coords)]
    min_z = min(c.z for c in cyl_coords_set)
    max_z = max(c.z for c in cyl_coords_set)
    height_range = max_z - min_z

    ball_pos = 0.0  # phase for sine wave

    while True:
        ball_height = (math.sin(ball_pos) + 1) / 2 * height_range + min_z

        for c in cyl_coords_set:
            # Ball appears red if within thickness, else white background
            if abs(c.z - ball_height) < BALL_THICKNESS:
                c.color = BALL_COLOR
            else:
                c.color = BACKGROUND_COLOR

            # Set LED color (GRB ordering)
            strip.setPixelColor(c.idx, Color(int(c.color[1]), int(c.color[0]), int(c.color[2])))

        strip.show()
        ball_pos += BOUNCE_SPEED
        time.sleep(FRAME_DELAY)

# ----------------- AUTO RUN -----------------
if __name__ == "__main__":
    bouncing_ball()
