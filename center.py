import time
import math
import random
import re
import numpy as np
from rpi_ws281x import PixelStrip, Color

# SETTINGS
LED_PIN = 18         # GPIO pin
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 255
LED_INVERT = False
LED_CHANNEL = 0

# EFFECT SETTINGS
max_brightness = 100
fade_speed = 5       # How fast it fades per cycle
expand_speed = 2.0   # How fast the "sphere" expands per cycle (units in coordinate space)

# HELPERS
def vectorNorm(v1, v2=[0,0,0]):
    return math.sqrt(sum((a-b)**2 for a,b in zip(v1,v2)))

def createRandomRGB():
    return [random.randint(0,max_brightness) for _ in range(3)]

def fadeColours(current, target, fadePerCycle=1.0):
    new_colour = current.copy()
    for i in range(3):
        if current[i] > target[i]+fadePerCycle:
            new_colour[i] -= fadePerCycle
        elif current[i] < target[i]-fadePerCycle:
            new_colour[i] += fadePerCycle
        else:
            new_colour[i] = target[i]
    return new_colour

# MAIN EFFECT
def xmaslight():
    # Load coordinates
    coordfilename = "coords_brackets.txt"
    with open(coordfilename,'r') as f:
        coords_raw = f.readlines()

    coords = []
    for line in coords_raw:
        vals = [int(re.sub(r'[^-\d]','', x)) for x in line.split(',')]
        coords.append(vals)

    coords_arr = np.array(coords, dtype=np.float64)
    center = coords_arr.mean(axis=0)
    coords_centered = coords_arr - center
    coords_list = coords_centered.tolist()

    # Strip setup
    PIXEL_COUNT = len(coords_list)
    strip = PixelStrip(PIXEL_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()

    black = [0,0,0]

    # Main loop
    while True:
        # New random color
        color = createRandomRGB()
        pixel_colors = [black.copy() for _ in coords_list]

        # Expand from center
        radius = 0
        max_radius = max(vectorNorm(coord) for coord in coords_list)

        while radius <= max_radius:
            for i, coord in enumerate(coords_list):
                if vectorNorm(coord) <= radius:
                    pixel_colors[i] = color.copy()
            # Update LEDs
            for i, c in enumerate(pixel_colors):
                strip.setPixelColor(i, Color(int(c[0]), int(c[1]), int(c[2])))
            strip.show()
            radius += expand_speed
            time.sleep(0.05)

        # Fade out
        fading = True
        while fading:
            fading = False
            for i in range(len(pixel_colors)):
                pixel_colors[i] = fadeColours(pixel_colors[i], black, fade_speed)
                if any(c > 0 for c in pixel_colors[i]):
                    fading = True
            for i, c in enumerate(pixel_colors):
                strip.setPixelColor(i, Color(int(c[0]), int(c[1]), int(c[2])))
            strip.show()
            time.sleep(0.05)

xmaslight()
