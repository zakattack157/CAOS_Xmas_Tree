# source ~/opencv-env/bin/activate

#import image_processing

import os
import time
import cv2
import numpy as np

NUM_PHOTOS = 649
SAVE_DIR = "xy"                        # change to zy after rotating tree
COORD_FILE = "coords/coords_xy.txt"    # change to coords_zy.txt after rotating

# creates folder if not there
os.makedirs(SAVE_DIR, exist_ok=True)

coord_file = open(COORD_FILE, "a")

# opens webcam
camera = cv2.VideoCapture(1)    # switch (1) to (0) if neccessary
time.sleep(1)

photo_index = 0

while photo_index <= NUM_PHOTOS:
    ret, frame = camera.read()
    if not ret:
        print("Failed to capture image.")
        break

    cv2.imshow("camera", frame)

    # press enter to save each image
    if cv2.waitKey(1) & 0xFF == 13:

        # converts to grayscale and blurs
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (9, 9), 0)

        # finds brightest pixel
        _, _, _, max_loc = cv2.minMaxLoc(blur)
        x, y = max_loc

        # draws circle on brightest pixel
        cv2.circle(frame, (x, y), 8, (0, 0, 255), 2)

        # saves marked image
        filename = f"light_{photo_index:03}.png"
        filepath = os.path.join(SAVE_DIR, filename)
        cv2.imwrite(filepath, frame)

        # saves x,y to coords.txt
        coord_file.write(f"{x},{y}\n")

        print(f"Saved {filepath} | brightest at ({x}, {y})")

        photo_index += 1
        time.sleep(0.5)

camera.release()
coord_file.close()
cv2.destroyAllWindows()
