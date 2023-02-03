
import cv2
import numpy as np
from pathlib import Path
from time import sleep

base_folder = Path(__file__).parent.resolve()
delay = 5
scalefactor = 2

image = cv2.imread('image._000 copy.jpg')

def display(image, image_name, delay=5, scalefactor=2):
    """convert the image into an array of the RGB values that make up each pixel"""
    image = np.array(image, dtype=float)/float(255)

    """scale the image by the factor specified (2 by default)"""
    shape = image.shape
    height = int(shape[0]/scalefactor)
    width = int(shape[1]/scalefactor)
    image = cv2.resize(image, (width, height))

    """display the image for the time period of the delay (5 seconds by default) and then close"""
    cv2.namedWindow(image_name)
    cv2.imshow(image_name, image)
    sleep(delay)
    cv2.destroyAllWindows()

def contrast_stretch(im):
    in_min = np.percentile(im, 5)
    in_max = np.percentile(im, 95)

    out_min = 0.0
    out_max = 255.0

    out = im - in_min
    out *= ((out_min - out_max) / (in_min - in_max))
    out += in_min
    
    return out

display(image, "original")
contrasted = contrast_stretch(image)
display(contrasted, "contrasted image")