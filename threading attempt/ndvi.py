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
    """
    This function takes an image, image name (string) as arguments, as well as a delay in seconds and a scale factor, both optional and defaulting to 5 and 2 respectively.
    It scales the image provided by the inverse of the scale factor and shows it for the amount of time specified by the delay or, optionally if the delay is specified to be -1, it shows the image until input by the user through a keyboard.
    Upon the end of the specified amount of time or user input, all windows are closed and the function ends, returning nothing.
    """
    image = np.array(image, dtype=float)/float(255)

    shape = image.shape
    height = int(shape[0]/scalefactor)
    width = int(shape[1]/scalefactor)
    image = cv2.resize(image, (width, height))
    cv2.namedWindow(image_name)
    cv2.imshow(image_name, image)
    if delay != -1:
        sleep(delay)
    else:
        cv2.waitKey(0)
    cv2.destroyAllWindows()


def contrast_stretch(im):
    """
    This function takes in an image as argument and, taking into account the min and max values of the pixels, it stretches the contrast of the image as to make small changes more evident.
    Upon completetion, it returns the processed image.
    If the image is a single colour, then the operation will throw a division by zero exception, since both the minimum and maximum values of the pixels are the same. This is taken into account and a try, except clause was added for that case.
    """
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
    """
    This function takes an image as argument.
    The image is processed according to NDVI calculation model, based on the reflectance of red and infrared radiation by healthy vegetation, returning a greyscale image representing the NDVI values from lowest (darkest) to highest (lightest).
    """
    b, g, r = cv2.split(image)
    bottom = (r.astype(float) + b.astype(float))
    bottom[bottom == 0] = 0.01
    ndvi = (b.astype(float) - r)/bottom
    return ndvi


def main(base_folder):
    """
    Looping through every file and folder in the current directory (without recursiveness),
    for every file with extension '.jpg' or '.jpeg', making sure not to process the same image twice or process an already NDVI image, it'll be processed into a greyscale NDVi image,
    which is saved in the same directory with a filename of the form {filename}_ndvi.png, where filename is the name of the original image.
    This is done continuously and without user input, with the elapsed time being calculated and printed to the console upon the termination of the loop.
    """

    start_time = datetime.now()
    files = os.listdir(base_folder)
    for image in files:

        if image.endswith(".jpg") or image.endswith(".jpeg"):
            original = cv2.imread(str(base_folder / str(image)))

            filename, extension = image.split(".", 1)
            if filename + "_ndvi.png" not in files and "ndvi" not in filename:
                print(f"processing {filename}")
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
    minutes, seconds = divmod(elapsed.days * 60*60*24 + elapsed.seconds, 60)
    print(f"{minutes} minutes and {seconds} seconds have passed")
    return minutes, seconds
