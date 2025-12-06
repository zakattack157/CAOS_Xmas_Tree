import time
import math
import random
import re
import numpy as np
from rpi_ws281x import PixelStrip, Color

# SETTINGS
LED_PIN = 18         # GPIO pin
LED_FREQ_HZ = 800000 # Usually 800kHz
LED_DMA = 10         # DMA channel
LED_BRIGHTNESS = 255 # 0-255
LED_INVERT = False
LED_CHANNEL = 0

# Sphere settings
max_brightness = 100
min_brightness = max_brightness // 2
number_of_spheres = 5

# HELPERS
def random3DValues(min_values, max_values, not_like_this=[]):
    if isinstance(min_values, (int,float)):
        min_values = [min_values]*3
    if isinstance(max_values, (int,float)):
        max_values = [max_values]*3
    new_values = []
    for i in range(3):
        new_values.append(random.randint(min_values[i], max_values[i]))
        if len(not_like_this) == 3 and abs(new_values[i]-not_like_this[i]) < (max_values[i]-min_values[i])*0.1:
            new_values[i] = min_values[i] + (new_values[i] + (max_values[i]-min_values[i])//2) % (max_values[i]-min_values[i])
    return new_values

def createRandomRGB(not_like_this=[]):
    new_colour = [random.randint(0,max_brightness) for _ in range(3)]
    if len(not_like_this) == 3:
        for i in range(3):
            if abs(new_colour[i]-not_like_this[i]) < max_brightness*0.1:
                new_colour[i] = (new_colour[i] + max_brightness//2) % max_brightness
    brightness = sum(new_colour)
    if brightness > max_brightness:
        new_colour = [c * max_brightness/brightness for c in new_colour]
    if brightness < min_brightness:
        if brightness <= 0:
            new_colour[random.randint(0,2)] = random.randint(1,max_brightness)
        else:
            new_colour = [c * min_brightness/brightness for c in new_colour]
    return new_colour

def addColours(col1, col2):
    new_colour = [c1**2 + c2**2 for c1,c2 in zip(col1,col2)]
    brightness = sum(new_colour)
    if brightness > max_brightness:
        new_colour = [c*max_brightness/brightness for c in new_colour]
    return new_colour

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

def vectorNorm(v1, v2=[0,0,0]):
    return math.sqrt(sum((a-b)**2 for a,b in zip(v1,v2)))


# MAIN
def xmaslight():
    coordfilename = "coords_brackets.txt"
    with open(coordfilename,'r') as f:
        coords_raw = f.readlines()

    coords = []
    pixel_colour = []
    for line in coords_raw:
        vals = [int(re.sub(r'[^-\d]','', x)) for x in line.split(',')]
        coords.append(vals)
        pixel_colour.append(createRandomRGB())

    coords_arr = np.array(coords, dtype=np.float64)
    center = coords_arr.mean(axis=0)
    coords_centered = coords_arr - center
    coords_list = coords_centered.tolist()

    min_coord = coords_centered.min(axis=0).tolist()
    max_coord = coords_centered.max(axis=0).tolist()
    max_size = max_coord[2] - min_coord[2]

    PIXEL_COUNT = len(coords_list)
    strip = PixelStrip(PIXEL_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()

    # Sphere initialization
    standard_step_size = 7/max_size
    standard_wave_width = 3
    slow = 0
    black = [0,0,0]

    sphere_colours = []
    sphere_rad_sizes = []
    sphere_coords = []
    sphere_step_size = []
    sphere_fade_modifier = []
    sphere_wave_width = []

    for i in range(number_of_spheres):
        sphere_colours.append(createRandomRGB())
        sphere_rad_sizes.append(-i*max_size/number_of_spheres)
        sphere_coords.append(random3DValues(min_coord,max_coord))
        sphere_step_size.append(random.gauss(1,0.25)*standard_step_size)
        sphere_fade_modifier.append(random.gauss(1,0.25))
        sphere_wave_width.append(random.gauss(1,0.3)*standard_wave_width)

    number_of_spheres_to_use = 1
    cycles = 0

    while True:
        time.sleep(slow)

        for idx in range(number_of_spheres_to_use):
            sphere_rad_sizes[idx] += max_size*sphere_step_size[idx]
            if sphere_rad_sizes[idx] > max_size:
                sphere_rad_sizes[idx] = -(0.15*(random.random()+0.5)*max_size)
                sphere_colours[idx] = createRandomRGB(sphere_colours[(idx+number_of_spheres_to_use-1)%number_of_spheres_to_use])
                sphere_coords[idx] = random3DValues(min_coord,max_coord,sphere_coords[(idx+number_of_spheres_to_use-1)%number_of_spheres_to_use])
                sphere_step_size[idx] = random.gauss(1,0.25)*standard_step_size
                sphere_fade_modifier[idx] = random.gauss(1,0.25)
                sphere_wave_width[idx] = random.gauss(1,0.25)*standard_wave_width
                cycles += 1

            for LED in range(len(coords_list)):
                norm = vectorNorm(coords_list[LED], sphere_coords[idx])
                if sphere_rad_sizes[idx]-norm < sphere_wave_width[idx]*max_size*sphere_step_size[idx] and sphere_rad_sizes[idx]-norm > max_size*sphere_step_size[idx]/sphere_wave_width[idx]:
                    pixel_colour[LED] = addColours(pixel_colour[LED],sphere_colours[idx])
                else:
                    pixel_colour[LED] = fadeColours(pixel_colour[LED],black, sphere_fade_modifier[idx]*number_of_spheres_to_use/2)

        # Update LEDs
        for LED in range(len(coords_list)):
            R,G,B = [int(c) for c in pixel_colour[LED]]
            strip.setPixelColor(LED, Color(R,G,B))
        strip.show()

        if cycles >= number_of_spheres_to_use:
            number_of_spheres_to_use = random.randint(1,number_of_spheres)
            cycles = 0


xmaslight()
