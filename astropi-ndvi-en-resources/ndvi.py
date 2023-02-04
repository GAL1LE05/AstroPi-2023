import cv2
import os
import numpy as np
from pathlib import Path
from time import sleep
from datetime import datetime

base_folder = Path(__file__).parent.resolve()
delay = 5
scalefactor = 2


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
    if delay != -1:
        sleep(delay)
    else:
        cv2.waitKey(0)
    cv2.destroyAllWindows()


def contrast_stretch(im):
    in_min = np.percentile(im, 5)
    in_max = np.percentile(im, 95)

    out_min = 0.0
    out_max = 255.0

    out = im - in_min
    try:
        out *= ((out_min - out_max) / (in_min - in_max))
    except ZeroDivisionError:
        out *= 255
    out += in_min
    return out


def calc_ndvi(image):
    b, g, r = cv2.split(image)
    bottom = (r.astype(float) + b.astype(float))
    bottom[bottom == 0] = 0.01
    ndvi = (b.astype(float) - r)/bottom
    return ndvi


start_time = datetime.now()

for image in os.listdir(base_folder):

    if image.endswith(".jpg") or image.endswith(".jpeg"):
        original = cv2.imread(str(base_folder / str(image)))

        filename, extension = image.split(".", 1)
        print(f"showing {filename}")
        # display(original, 'Original', -1)
        contrasted = contrast_stretch(original)
        # display(contrasted, 'Contrasted Original', -1)
        ndvi = calc_ndvi(contrasted)
        # display(ndvi, 'NDVI', -1)
        ndvi_contrasted = contrast_stretch(ndvi)
        # display(ndvi_contrasted, 'NDVI Contrasted', -1)
        cv2.imwrite(str(base_folder / str(filename + '_ndvi.png')),
                    ndvi_contrasted)

finish_time = datetime.now()
elapsed = finish_time - start_time
print(elapsed)
elapsed_tuple = divmod(elapsed.days * 60*60*24 + elapsed.seconds, 60)
print(f"{elapsed_tuple[0]} minutes and {elapsed_tuple[1]} seconds have passed")
