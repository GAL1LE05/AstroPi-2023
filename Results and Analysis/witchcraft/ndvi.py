import cv2
import os
import numpy as np
from pathlib import Path
from time import sleep
from datetime import datetime
import fastiecm

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
    min = np.percentile(im, 1)
    max = np.percentile(im, 99)
    out_min = 0.0
    out_max = 255.0

    out = im - in_min
    try:
        out *= ((out_min - out_max) / (in_min - in_max))
    except ZeroDivisionError:
        out *= 255
    out += in_min
    return out, max, min


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

"""
Looping through every file and folder in the current directory (without recursiveness),
for every file with extension '.jpg' or '.jpeg', it'll be processed into a greyscale NDVi image,
which is saved in the same directory with a filename of the form {filename}_ndvi.png, where filename is the name of the original image.
This is done continuously and without user input, with the elapsed time being calculated and printed to the console upon the termination of the loop.
"""

start_time = datetime.now()
img_data_file = base_folder / "image_data.csv"

for image in os.listdir(base_folder):

    if image.endswith(".jpg") or image.endswith(".jpeg"):
        with open(img_data_file, 'a') as df:
            original = cv2.imread(str(base_folder / str(image)))

            filename, extension = image.split(".", 1)
            print(f"processing {filename}")
            # display(original, 'Original', -1)
            # contrasted = contrast_stretch(original)
            # display(contrasted, 'Contrasted Original', -1)
            ndvi = calc_ndvi(original)
            # display(ndvi, 'NDVI', -1)
            ndvi_contrasted, max, min = contrast_stretch(ndvi)
            print(f"Max NDVI value for {filename}: {max}\nMin NDVI value for {filename}: {min}")
            # display(ndvi_contrasted, 'NDVI Contrasted', -1)
            cv2.imwrite(str(base_folder / str(filename + '_ndvi.png')),
                        ndvi_contrasted)
            #color_mapped_prep = ndvi.astype(np.uint8)*127+128
            #color_mapped_image = cv2.applyColorMap(color_mapped_prep, fastiecm.fastiecm[::-1])
            #cv2.imwrite(str(base_folder / str(filename + '_ndvi_cm.png')), color_mapped_image)
            df.write(
            f"{filename}; {min}; {max} \n")
            df.flush()
            os.fsync(df.fileno())

finish_time = datetime.now()
elapsed = finish_time - start_time
print(elapsed)
minutes, seconds = divmod(elapsed.days * 60*60*24 + elapsed.seconds, 60)
print(f"{minutes} minutes and {seconds} seconds have passed")
