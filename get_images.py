# source ~/opencv-env/bin/activate

import image_processing

import matplotlib.pyplot as plt
import cv2
import time
import os
import numpy as np

NUM_PHOTOS = 649
DELAY_MS = 1000
SAVE_DIR = "xy" # change to zy after rotating tree

camera = cv2.VideoCapture(1)
#time.sleep(3)   # gives camera time to focus

photo_index = 0

while photo_index <= NUM_PHOTOS:
    ret, frame = camera.read()
    #gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if not ret:
        print("Failed to get photo")
        break

    cv2.imshow('test', frame)  # displays camera

    # press enter to save each photo
    if cv2.waitKey(1) & 0xFF == 13:
        filename = f"light_{photo_index:03}.png"
        filepath = os.path.join(SAVE_DIR, filename)

        cv2.imwrite(filepath, frame)
        print(f"Saved {filepath}")
        photo_index += 1
        time.sleep(1)

camera.release()
cv2.destroyAllWindows()