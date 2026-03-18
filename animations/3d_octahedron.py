def xmaslight():
    # This is the code from my 
    
    #NOTE THE LEDS ARE GRB COLOUR (NOT RGB)
    
    # Here are the libraries I am currently using:
    import time
    import re
    import math
    
    # You are welcome to add any of these:
    import random
    import numpy as np
    from rpi_ws281x import PixelStrip, Color
    # import scipy
    # import sys

    # If you want to have user changable values, they need to be entered from the command line
    # so import sys sys and use sys.argv[0] etc
    # some_value = int(sys.argv[0])
    
    # IMPORT THE COORDINATES (please don't break this bit)
    
    coordfilename = "coords_brackets.txt"
	
    fin = open(coordfilename,'r')
    coords_raw = fin.readlines()
    
    coords_bits = [i.split(",") for i in coords_raw]
    
    coords = []
    
    for slab in coords_bits:
        new_coord = []
        for i in slab:
            new_coord.append(int(re.sub(r'[^-\d]','', i)))
        coords.append(new_coord)

    LED_COUNT = len(coords)
    LED_PIN = 18         # GPIO pin
    LED_FREQ_HZ = 800000 # Usually 800kHz
    LED_DMA = 10         # DMA channel
    LED_BRIGHTNESS = 255 # 0-255
    LED_INVERT = False   # True if using inverting logic
    LED_CHANNEL = 0      # Usually 0

    strip = PixelStrip(
        LED_COUNT,
        LED_PIN,
        LED_FREQ_HZ,
        LED_DMA,
        LED_INVERT,
        LED_BRIGHTNESS,
        LED_CHANNEL
    )
    strip.begin()    
    
    # YOU CAN EDIT FROM HERE DOWN
    
    # I get a list of the coordinates which is not overly useful here other than to set the max and min coordinates
    xs = []
    ys = []
    zs = []
    for i in coords:
        xs.append(i[0])
        ys.append(i[1])
        zs.append(i[2])

    slow = 0

    ballradius = 220

    # the eight colours in GRB order
    # if you are turning a lot of them on at once, keep their brightness down please
    colourA = [0,50,0] # red
    colourB = [40,60,0] # orange
    colourC = [45, 45, 0]  # yellow
    colourD = [38, 0, 0]  # green
    colourE = [38, 0, 38]  # teal
    colourF = [0, 0, 38]  # blue
    colourG = [0, 13, 38]  # indigo
    colourH = [0, 25, 38]  # violet

    # Helper: convert [R,G,B] to Color(G,R,B) because LEDs are GRB
    def GRB(col):
        return Color(col[1], col[0], col[2])

    run = 1

    coords_arr = np.array(coords, dtype=np.float64)

    # centers around origin 
    center = coords_arr.mean(axis=0)
    coords_centered = coords_arr - center

    coordmat = np.asmatrix(coords_centered).transpose()


    cnt = 0
    
    while run == 1:
        
        time.sleep(slow)
        
        LED = 0
        while LED < len(coords):

            # Check which octant LED lives in to generate colored octahedron
            if coordmat[0, LED]**2 + coordmat[1, LED]**2 + coordmat[2, LED]**2 < ballradius**2:

                if coordmat[0, LED] < 0:
                    if coordmat[1, LED] < 0:
                        if coordmat[2, LED] < 0:
                            strip.setPixelColor(LED, GRB(colourA))
                        else:
                            strip.setPixelColor(LED, GRB(colourB))
                    else:
                        if coordmat[2, LED] < 0:
                            strip.setPixelColor(LED, GRB(colourC))
                        else:
                            strip.setPixelColor(LED, GRB(colourD))
                else:
                    if coordmat[1, LED] < 0:
                        if coordmat[2,LED] < 0:
                            strip.setPixelColor(LED, GRB(colourE))
                        else:
                            strip.setPixelColor(LED, GRB(colourF))
                    else:
                        if coordmat[2, LED] < 0:
                            strip.setPixelColor(LED, GRB(colourG))
                        else:
                            strip.setPixelColor(LED, GRB(colourH))

            LED += 1

        # use the show() option as rarely as possible as it takes ages
        # do not use show() each time you change a LED but rather wait until you have changed them all
        strip.show() ## Dan Walsh had to comment this out since he doesn't have LEDs. Won't work until hardware is available.
        
        # now we get ready for the next cycle
        # We do this similarly to how Matt did his translating plane effect: use a static spatial coloring function,
        # but rotate all of the LEDs!

        #Do rotate-y stuff here
        #Rotation Matrix

        # Small scalar amount (in radians) to rotate for one timestep of animation (plays role of "inc" variable in Matt's original code)
        theta = 0.2

        # UNIT vector axis about which to rotate for one timestep of animation
        if cnt%100 == 0: #Switch up the rotation axis every so often to keep things interesting
            ux = random.uniform(-1.0, 1.0)
            uy = random.uniform(-1.0, 1.0)
            uz = random.uniform(-1.0, 1.0)

            length = math.sqrt(ux**2+uy**2+uz**2)

            ux = ux / length
            uy = uy / length
            uz = uz / length

            u = np.matrix(
                [
                    [ux],
                    [uy],
                    [uz]
                ]
            )

        UX = np.matrix( #Cross Product Matrix
            [
                [0., -uz, uy],
                [uz, 0., -ux],
                [-uy, ux, 0.]
            ]
        )

        UXU = np.matmul(u,u.transpose()) #Generate Outer Product

        I = np.matrix( #Identity Matrix
            [
                [1., 0., 0.],
                [0., 1., 0.],
                [0., 0., 1.]
            ]
        )

        # Setup rotation matrix using R = cos(theta) I + sin(theta) UX + (1 - cos(theta)) UXU (Rodrigues' Rotation Formula)
        RotMat = np.cos(theta) * I + np.sin(theta) * UX + (1 - np.cos(theta)) * UXU

        coordmat = np.matmul(RotMat,coordmat) #Rotate all LEDs on tree according to RotMat
        cnt += 1

    return 'DONE'


# yes, I just put this at the bottom so it auto runs
xmaslight()
