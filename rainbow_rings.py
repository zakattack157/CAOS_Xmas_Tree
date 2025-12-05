# Here are the libraries I am currently using:
import time
import re
import math
import numpy as np

from rpi_ws281x import PixelStrip, Color
USE_PLOT = False

# Superior cylindrical coordinate system
class cyl_coords:
    def __init__(self, coords, idx):
        # coords = [x, y, z]
        self.r = math.sqrt(coords[0]**2 + coords[1]**2)

        # FIXED to standard atan2(y, x)
        self.theta = math.atan2(coords[1], coords[0])

        self.z = coords[2]
        self.color = [0, 0, 0]
        self.idx = idx

    def rotate(self, rotation):
        new_rotation = (self.theta + rotation)

        # wrap angle into [-pi, pi]
        while new_rotation > np.pi:
            new_rotation -= 2*np.pi
        while new_rotation < -np.pi:
            new_rotation += 2*np.pi

        self.theta = new_rotation

    def get_coords(self):
        x = self.r * math.cos(self.theta)
        y = self.r * math.sin(self.theta)
        z = self.z
        return [x, y, z]


def xmaslight():

    coordfilename = "coords_brackets.txt"

    # Read in coordinates and strip garbage chars
    fin = open(coordfilename, 'r')
    coords_raw = fin.readlines()
    coords_bits = [i.split(",") for i in coords_raw]

    coords = []
    for slab in coords_bits:
        new_coord = []
        for i in slab:
            new_coord.append(int(re.sub(r'[^-\d]', '', i)))
        coords.append(new_coord)

    PIXEL_COUNT = len(coords)

    # --- rpi_ws281x PixelStrip setup ---
    LED_PIN = 18
    LED_FREQ_HZ = 800000
    LED_DMA = 10
    LED_INVERT = False
    LED_BRIGHTNESS = 255
    LED_CHANNEL = 0

    strip = PixelStrip(
        PIXEL_COUNT, LED_PIN,
        LED_FREQ_HZ, LED_DMA,
        LED_INVERT, LED_BRIGHTNESS,
        LED_CHANNEL
    )

    strip.begin()

    rainbow_lights(strip, coords)

    return "DONE"


def rainbow_lights(strip, coords):

    # Build cylindrical coordinate objects
    cyl_coords_set = []
    max_z = -1e9
    min_z = 1e9

    for i in range(len(coords)):
        c = cyl_coords(coords[i], i)
        cyl_coords_set.append(c)
        max_z = max(max_z, c.z)
        min_z = min(min_z, c.z)

    # Color list (GRB format in this LED strip)
    # [G,R,B]
    colors = [
        [0, 30, 0],
        [15, 15, 0],
        [30, 0, 0],
        [0, 15, 15],
        [0, 0, 30],
        [15, 0, 15]
    ]

    ring_height = (max_z - min_z) / (len(colors) - 1)

    inc = 0
    rot = np.pi / 18.0    # 10° rotation each frame

    while True:

        # Write LEDs
        for c in cyl_coords_set:
            # GRB ordering for Color()
            g = int(c.color[0])
            r = int(c.color[1])
            b = int(c.color[2])
            strip.setPixelColor(c.idx, Color(g, r, b))

        strip.show()

        # Update colors & rotate
        for c in cyl_coords_set:
            z_bin = (round((c.z - min_z)/ring_height) + inc) % len(colors)

            c.rotate(rot)

            # compute intensity modulation
            adjusted_rotation = (c.theta + np.pi/6.0 * z_bin) % (2*np.pi)
            intensity = adjusted_rotation / (np.pi)

            base_col = np.array(colors[z_bin])
            new_col = np.array(base_col) * intensity

            c.color = np.clip(np.rint(new_col), 0, 255)

        inc = (inc + 1) % len(colors)

        time.sleep(0.03)
        

# Auto-run
if __name__ == "__main__":
    xmaslight()
