import cv2
import numpy as np
from pathlib import Path
from time import sleep

base_folder = Path(__file__).parent.resolve()
delay = 5
scalefactor = 2

image = cv2.imread('./1st Test Run/image._000.jpg')

def display(image, image_name, delay=5, scalefactor=2):
    """convert the image into an array of the RGB values that make up each pixel"""
    image = np.array(image, dtype=float)/float(255)

    """scale the image by the factor specified (2 by default)"""
    shape = image.shape
    height = int(shape[0]/scalefactor)
    width = int(shape[1]/scalefactor)
    image = cv2.resize(image, (width, height))

    """display the image for the time period of the delay (5 seconds by default) and then close"""
    cv2,namedWindow(image_name)
    cv2.imshow(image_name, image)
    sleep(delay)
    cv2.destroyAllWindows()