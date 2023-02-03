import cv2
import numpy as np
from pathlib import Path
from time import sleep

base_folder = Path(__file__).parent.resolve()
delay = 5
scalefactor = 2

original = cv2.imread(r'C:\Users\LENOVO\Documents\AstroPi-2023\test_image98.jpeg')


def display(image, image_name):
    image = np.array(image, dtype=float)/float(255)
    shape = image.shape
    height = int(shape[0]/2)
    width = int(shape[1]/2)
    image = cv2.resize(image, (width, height))
    cv2.namedWindow(image_name)
    cv2.imshow(image_name, image)
    cv2.waitKey(0)
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


def calc_ndvi(image):
    b, g, r = cv2.split(image)
    bottom = (r.astype(float) + b.astype(float))
    bottom[bottom == 0] = 0.01
    ndvi = (r.astype(float) - b)/bottom
    return ndvi


display(original, 'Original')
contrasted = contrast_stretch(original)
display(contrasted, 'Contrasted Original')
ndvi = calc_ndvi(contrasted)
display(ndvi, 'NDVI')
ndvi_contrasted = contrast_stretch(ndvi)
display(ndvi_contrasted, 'NDVI Contrasted')
color_mapped_prep = ndvi_contrasted.astype(np.uint8)
