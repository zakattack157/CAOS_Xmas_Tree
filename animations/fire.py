def xmaslight():
    # This is the code from my

    # NOTE THE LEDS ARE GRB COLOUR (NOT RGB)

    from rpi_ws281x import PixelStrip, Color

    PIXEL_COUNT = len(coords)
    LED_PIN = 18         # GPIO pin
    LED_FREQ_HZ = 800000 # Usually 800kHz
    LED_DMA = 10         # DMA channel
    LED_BRIGHTNESS = 255 # 0-255
    LED_INVERT = False   # True if using inverting logic
    LED_CHANNEL = 0      # Usually 0

    strip = PixelStrip(PIXEL_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()

    # IMPORT THE COORDINATES (please don't break this bit)

    coordfilename = "coords_brackets.txt"

    fin = open(coordfilename, 'r')
    coords_raw = fin.readlines()

    coords_bits = [i.split(",") for i in coords_raw]

    coords = []

    for slab in coords_bits:
        new_coord = []
        for i in slab:
            new_coord.append(int(re.sub(r'[^-\d]', '', i)))
        coords.append(new_coord)

    # set up the pixels (AKA 'LEDs')
    PIXEL_COUNT = len(coords)  # this should be 500

    pixels = neopixel.NeoPixel(board.D18, PIXEL_COUNT, auto_write=False)

    # YOU CAN EDIT FROM HERE DOWN

    # I get a list of the heights which is not overly useful here other than to set the max and min altitudes
    heights = []
    for i in coords:
        heights.append(i[2])

    min_alt = min(heights)
    max_alt = max(heights)

    # VARIOUS SETTINGS

    # Max brightness  (0 - 255)
    max_brightness = 50

    # how quickly the flames animate
    speed = 0.4

    # size of negative-flame particles
    radius_sq = 0.1

    # number of negative-flame particles
    num_particles = 50

    class Particle:
        def __init__(self):
            self.x = random.random()*math.pi*2.0
            self.y = random.random()*2.0 - 0.5
            self.dx = (random.random()-0.5)*0.1

        def step(self, t):
            self.y += 0.1*t
            self.x += self.dx*t
            if self.y > 1.5:
                self.y -= 2.0

        def dist_sq(self, x, y):
            dx = (self.x + math.pi - x) % (2.0*math.pi) - math.pi
            dy = self.y - y
            return dx*dx + dy*dy

        def value_at(self, x, y):
            scale = self.y + 1.0
            f = self.dist_sq(x, y) / (radius_sq * scale * scale)
            if f < 1.0:
                return (1.0 - f*f)*self.y
            else:
                return 0.0

    # Create the particles
    particles = [Particle() for _ in range(num_particles)]

    # Get 2D flame colour
    # x: 0 - 2pi
    # y: 0 - 1
    def get_colour(x, y):
        result = y*0.5
        for p in particles:
            result += p.value_at(x, y)
        brightness = 1.0 - min(max(result-0.2, 0.0), 1.0)

        if brightness > 0.95:
            return [max_brightness, max_brightness, (brightness-0.95)*max_brightness/0.05]
        elif brightness > 0.85:
            return [(brightness-0.85)*max_brightness/0.1, max_brightness, 0.0]
        else:
            return [0.0, brightness*max_brightness/0.85, 0.0]

    # Get 3D flame colour (unwrap 2D plane from around cone)
    def get_colour_3d(x, z, y):
        theta = math.atan2(x, z)
        return get_colour(theta, (y - min_alt)/(max_alt - min_alt))

    # advance particle positions
    def step_particles():
        for p in particles:
            p.step(speed)

    def GRB_to_RGB(grb):
        return Color(grb[1], grb[0], grb[2])

    # yes, I just run which run is true
    run = 1
    while run == 1:
        LED = 0
        while LED < len(coords):
            coord = coords[LED]
            strip.setPixelColor(LED, GRB_to_RGB(colourA))
            LED += 1

        # use the show() option as rarely as possible as it takes ages
        # do not use show() each time you change a LED but rather wait until you have changed them all
        strip.show()

        # now we get ready for the next cycle
        step_particles()

    return 'DONE'


# yes, I just put this at the bottom so it auto runs
xmaslight()