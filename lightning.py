import math
import random
import sys

# ----------------- GLOBAL SETTINGS -----------------

default_max_brightness = 100
max_brightness = default_max_brightness
min_max_brightness = 10
max_max_brightness = 254

min_brightness = math.floor(max_brightness * 0.8)

default_number_of_forks = 5
number_of_forks = default_number_of_forks
min_number_of_forks = 2
max_number_of_forks = 15

default_speed = 5
speed = default_speed
min_speed = 1
max_speed = 10

black = [0, 0, 0]


# ----------------- COMMAND LINE ARG PROCESSING -----------------

def usage():
    print(sys.argv[0] +
          " maximum_brightness(Default " + str(default_max_brightness) +
          ", Range " + str(min_max_brightness) + "-" + str(max_max_brightness) +
          ") maximum_number_of_forks(Default " + str(default_number_of_forks) +
          ", Range " + str(min_number_of_forks) + "-" + str(max_number_of_forks) +
          ") speed(Default " + str(default_speed) +
          ", Range " + str(min_speed) + "-" + str(max_speed) + ")")


if (len(sys.argv) > 1 and len(sys.argv) < 5) and sys.argv[1].isnumeric():
    max_brightness = float(sys.argv[1])
    if max_brightness > max_max_brightness or max_brightness < min_max_brightness:
        print("Error with arguments, brightness not valid: " + str(sys.argv))
        usage()
        quit()

    if len(sys.argv) >= 3 and sys.argv[2].isdigit():
        number_of_forks = int(sys.argv[2])
        if number_of_forks > max_number_of_forks or number_of_forks < min_number_of_forks:
            print("Error with arguments, number of forks not valid: " + str(sys.argv))
            usage()
            quit()

    if len(sys.argv) >= 4 and sys.argv[3].isnumeric():
        speed = float(sys.argv[3])
        if speed > max_speed or speed < min_speed:
            print("Error with arguments, speed not valid: " + str(sys.argv))
            usage()
            quit()

else:
    if len(sys.argv) > 1:
        print("Error with arguments: " + str(sys.argv))
        usage()
        quit()


# ----------------- UTILITY FUNCTIONS -----------------

def random3DValues(min_values, max_values, not_like_this=[]):
    if type(min_values) in (int, float):
        min_values = [min_values] * 3
    if type(max_values) in (int, float):
        max_values = [max_values] * 3

    new_values = []
    for i in range(3):
        diff = max_values[i] - min_values[i]
        val = random.randint(min_values[i], max_values[i])

        if len(not_like_this) == 3 and abs(val - not_like_this[i]) < diff * 0.1:
            val = min_values[i] + (val + diff / 2) % diff

        new_values.append(val)

    return new_values


def createRandomGRBColour(not_like_this=[]):
    new_colour = []
    brightness = 0

    for i in range(3):
        val = random.randint(0, max_brightness)

        if len(not_like_this) == 3 and abs(val - not_like_this[i]) < max_brightness * 0.1:
            val = (val + max_brightness / 2) % max_brightness

        new_colour.append(val)
        brightness += val

    if brightness > max_brightness:
        for i in range(3):
            new_colour[i] *= max_brightness / brightness

    if brightness < min_brightness:
        if brightness <= 0:
            new_colour[random.randint(0, 2)] = random.randint(1, max_brightness)
        else:
            for i in range(3):
                new_colour[i] *= min_brightness / brightness

    return new_colour


def addColours(colour1, colour2, percentageOnSecond=100):
    new = []
    brightness = 0

    for i in range(3):
        val = (colour1[i] * colour1[i] +
               colour2[i] * colour2[i] * percentageOnSecond / 100)
        new.append(val)
        brightness += val

    if brightness > max_brightness:
        for i in range(3):
            new[i] *= max_brightness / brightness

    return new


def fadeColours(currentColour, fadeToColour, fadePerCycle=1.0):
    new = currentColour.copy()
    for i in range(3):
        if currentColour[i] > fadeToColour[i] + fadePerCycle:
            new[i] -= fadePerCycle
        elif currentColour[i] < fadeToColour[i] - fadePerCycle:
            new[i] += fadePerCycle
        else:
            new[i] = fadeToColour[i]
    return new


def vectorNorm(a, b=[0, 0, 0]):
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


# ----------------- MAIN LIGHTNING ROUTINE -----------------

def xmaslight():

    # -------- FIXED IMPORTS FOR rpi_ws281x --------
    import time
    import re
    from rpi_ws281x import PixelStrip, Color

    # -------- Load Coordinates --------
    coordfilename = "coords_brackets.txt"
    coords_raw = open(coordfilename).readlines()
    coords_bits = [i.split(",") for i in coords_raw]

    coords = []
    pixel_colour = []

    for slab in coords_bits:
        c = []
        for i in slab:
            c.append(int(re.sub(r'[^-\d]', '', i)))
        coords.append(c)
        pixel_colour.append(createRandomGRBColour())

    # -------- Find Min/Max Coordinates --------
    max_coord = coords[0].copy()
    min_coord = coords[0].copy()

    # ********** FIXED: FIND HIGHEST Z VALUES **********
    # Build a sorted list of the highest Z-value LEDs (fork starting points)
    top_coord_indices = sorted(
        range(len(coords)),
        key=lambda i: coords[i][2],
        reverse=True
    )[:max_number_of_forks]
    # ***************************************************

    # Expand min/max coord
    for coord in coords:
        for i in range(3):
            max_coord[i] = max(max_coord[i], coord[i])
            min_coord[i] = min(min_coord[i], coord[i])

    # -------- SETUP LED STRIP (rpi_ws281x) --------
    PIXEL_COUNT = len(coords)
    LED_PIN = 18
    LED_FREQ_HZ = 800000
    LED_DMA = 10
    LED_INVERT = False
    LED_CHANNEL = 0
    LED_STRIP = None  # default WS2811/2812

    strip = PixelStrip(
        PIXEL_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT,
        int(max_brightness), LED_CHANNEL, LED_STRIP
    )
    strip.begin()

    # -------- HEIGHTS --------
    heights = [i[2] for i in coords]
    min_alt = min(heights)
    max_alt = max(heights)
    max_size = abs(max_alt - min_alt)

    # -------- Animation Settings --------
    standard_step_size = PIXEL_COUNT * speed ** 1.8 / 300
    standard_fade_time = PIXEL_COUNT * speed ** 0.5 / 5000
    max_search_radius = max_size / number_of_forks

    slow = 0
    number_of_forks_to_use = number_of_forks
    cycles = 0

    # -------- Fork Initialization --------
    fork_colours = []
    fork_search_sizes = []
    fork_coords_indices = []
    fork_step_size = []
    fork_fade_modifier = []

    for i in range(number_of_forks):
        fork_colours.append(createRandomGRBColour())
        fork_search_sizes.append(-i * (random.random() + 0.5) * standard_step_size)
        fork_coords_indices.append([top_coord_indices[i]])
        fork_step_size.append(random.gauss(1, 0.25) * standard_step_size)
        fork_fade_modifier.append(random.gauss(1, 0.25) * standard_fade_time)

    # ---------------- MAIN LOOP ----------------
    run = True
    while run:
        time.sleep(slow)

        max_search_radius = max_size / math.sqrt(number_of_forks_to_use)

        for i in range(number_of_forks_to_use):

            fork_search_sizes[i] += fork_step_size[i]

            if fork_search_sizes[i] > max_search_radius:
                fork_search_sizes[i] = -(random.random() + 0.5) * standard_step_size
                fork_colours[i] = createRandomGRBColour(fork_colours[(i - 1) % number_of_forks_to_use])

                fork_coords_indices[i] = [top_coord_indices[i]]
                pixel_colour[top_coord_indices[i]] = addColours(pixel_colour[top_coord_indices[i]], fork_colours[i])

                fork_step_size[i] = random.gauss(1, 0.25) * standard_step_size
                fork_fade_modifier[i] = random.gauss(1, 0.25) * number_of_forks_to_use * standard_fade_time
                cycles += 1

            last = fork_coords_indices[i][-1]

            # Fade old pixels
            j = 0
            while j < len(fork_coords_indices[i]):
                idx = fork_coords_indices[i][j]
                pixel_colour[idx] = fadeColours(pixel_colour[idx], black, fork_fade_modifier[i])

                if vectorNorm(pixel_colour[idx]) < 1:
                    fork_coords_indices[i].pop(j)
                else:
                    j += 1

            # Search for neighbours
            hits = []
            for LED in range(len(coords)):
                if coords[LED][2] > coords[last][2] and LED != last:
                    d = vectorNorm(coords[LED], coords[last])
                    if d < fork_search_sizes[i]:
                        hits.append(LED)
                        pixel_colour[LED] = addColours(pixel_colour[LED], fork_colours[i], 5)
                        fork_coords_indices[i].append(LED)

            # Collapse many hits into one
            if len(hits) > 10 * min_number_of_forks / (number_of_forks_to_use * speed):
                while len(hits) > 1:
                    norm1 = vectorNorm(pixel_colour[hits[0]]) / (coords[hits[0]][2] - min_coord[2] + 1)
                    norm2 = vectorNorm(pixel_colour[hits[1]]) / (coords[hits[1]][2] - min_coord[2] + 1)

                    if norm1 == norm2:
                        hits.pop(random.randint(0, 1))
                    else:
                        keep = 0 if norm1 > norm2 else 1
                        pixel_colour[hits[keep]] = addColours(pixel_colour[hits[keep]], fork_colours[i])
                        hits.pop(1 - keep)

                fork_search_sizes[i] = -(random.random() + 0.5) * standard_step_size
                fork_coords_indices[i] = [hits[0]]
            else:
                for h in hits:
                    if h in fork_coords_indices[i] and h != last:
                        fork_coords_indices[i].remove(h)

            # Write pixels
            for idx in fork_coords_indices[i]:
                c = pixel_colour[idx]
                strip.setPixelColor(idx, Color(int(c[1]), int(c[0]), int(c[2])))

        strip.show()

        if cycles >= number_of_forks_to_use:
            number_of_forks_to_use = random.randint(min_number_of_forks, number_of_forks)
            cycles = 0


# ----------------- AUTO RUN -----------------
xmaslight()
