import numpy as np
import matplotlib as plt
from PIL import Image

def convert_to_greyscale():

	#Load image using PIL
	img = Image.open('xy/light_000.png')

	#Convert img to NumPy array
	img_array = np.array(img)

	#Grayscale conversion formula: Y= 0.299*R + 0.587*G + 0.114*B
	gray_img = np.dot (img_array[..., :3], [0.299, 0.587, 0.114])

	brightest_pixel = gray_img.max()

	coords = np.unravel_index(np.argmax(gray_img), gray_img.shape)
	print("brightest coordinates:", coords)


convert_to_greyscale()