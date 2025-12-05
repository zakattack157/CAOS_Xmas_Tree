import time
import re
import math
import numpy as np
from rpi_ws281x import PixelStrip, Color

# ----------------- SETTINGS -----------------
USE_PLOT = False  # Not using plotting for LEDs

# LED strip configuration:
LED_PIN = 18
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_INVERT = False
LED_CHANNEL = 0
MAX_BRIGHTNESS = 100  # You can adjust this
UPDATE_DELAY = 0.05   # Seconds per frame (adjust speed)

# ----------------- CYLINDRICAL COORDS -----------------
class cyl_coords:
    def __init__(self, coords, idx):
        self.r = math.sqrt(coords[0]**2 + coords[1]**2)
        self.theta = math.atan2(coords[1], coords[0])  # y, x
        self.z = coords[2]
        self.color = [0, 0, 0]  # GRB
        self.idx = idx

    def rotate(self, rotation):
        new_rotation = self.theta + rotation
        while new_rotation > np.pi:
            new_rotation -= 2*np.pi
        while new_rotation < -np.pi:
            new_rotation += 2*np.pi
        self.theta = new_rotation

# ----------------- MAIN FUNCTION -----------------
def xmaslight():
    # Load coordinates
    coordfilename = "coords_brackets.txt"
    with open(coordfilename, 'r') as fin:
        coords_raw = fin.readlines()
    coords_bits = [line.split(",") for line in coords_raw]

    coords = []
    for slab in coords_bits:
        new_coord = [int(re.sub(r'[^-\d]', '', i)) for i in slab]
        coords.append(new_coord)

    PIXEL_COUNT = len(coords)

    # Initialize LED strip
    strip = PixelStrip(
        PIXEL_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT,
        MAX_BRIGHTNESS, LED_CHANNEL
    )
    strip.begin()

    rainbow_lights(strip, coords)

# ----------------- RAINBOW SPIRAL -----------------
def rainbow_lights(strip, coords):
    cyl_coords_set = []
    max_z = -10000
    min_z = 10000

    for i, coord in enumerate(coords):
        c = cyl_coords(coord, i)
        cyl_coords_set.append(c)
        max_z = max(max_z, c.z)
        min_z = min(min_z, c.z)

    # GRB Colors
    colors = np.array([
        [0, 30, 0],
        [15, 15, 0],
        [30, 0, 0],
        [0, 15, 15],
        [0, 0, 30],
        [15, 0, 15]
    ])
    ring_height = (max_z - min_z) / (len(colors) - 1)

    rot = np.pi / 18.0  # 10 degrees per frame
    inc = 0

    while True:
        # Update LED colors
        for c in cyl_coords_set:
            z_bin = (round((c.z - min_z)/ring_height) + inc) % len(colors)
            z_bin = max(min(z_bin, len(colors)-1), 0)

            c.rotate(rot)
            adjusted_rotation = (c.theta + np.pi/6.0 * z_bin) % (2.0 * np.pi)
            intensity = adjusted_rotation / np.pi  # Scale 0–2

            c.color = np.clip(np.rint(colors[z_bin] * intensity), 0, 255)

            # GRB ordering
            strip.setPixelColor(c.idx, Color(int(c.color[1]), int(c.color[0]), int(c.color[2])))

        strip.show()
        inc = (inc + 1) % len(colors)
        time.sleep(UPDATE_DELAY)  # Control speed of animation

# ----------------- AUTO RUN -----------------
if __name__ == "__main__":
    xmaslight()
