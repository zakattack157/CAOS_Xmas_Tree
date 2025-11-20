# source ~/opencv-env/bin/activate

import matplotlib.pyplot as plt
import cv2
import time
import numpy as np

cap = cv2.VideoCapture(1)
time.sleep(3)   # gives camera time to focus
ret, frame = cap.read()


while(True):
        cv2.imshow('test', frame) # displays image
        if cv2.waitKey(1) & 0xFF == ord('y'):
                cv2.imwrite('images/c1.png', frame)
                cv2.destroyAllWindows()
                break
cap.release()