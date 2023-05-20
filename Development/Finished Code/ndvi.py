import cv2
import os
import numpy as np
from pathlib import Path
from time import sleep
from datetime import datetime
import fastiecm


def display(image, image_name, delay=5, scale_factor=2):
    """
    This function takes an array of pixel values, `image`, a string 
    `image_name, as arguments, as well as an integer `delay` in
    seconds and another integer `scale factor`, both optional
    and defaulting to 5 and 2 respectively.

    It scales the image provided by the inverse of the scale factor and
    shows it for the amount of time specified by the delay or, optionally
    if the delay is specified to be -1, it shows the image until input
    by the user through a keyboard.

    Upon the end of the specified amount of time or user input,
    all windows are closed and the function ends, returning nothing.
    """
    image = np.array(image, dtype=float)/float(255)

    shape = image.shape
    height = int(shape[0]/scale_factor)
    width = int(shape[1]/scale_factor)
    image = cv2.resize(image, (width, height))
    cv2.namedWindow(image_name)
    cv2.imshow(image_name, image)
    if delay != -1:
        sleep(delay)
    else:
        cv2.waitKey(0)
    cv2.destroyAllWindows()


def contrast_stretch(image):
    """
    This function takes in an array of pixel values, `image` as argument
    and, taking into account the min and max values of the pixels, it
    increases the contrast of the image as to make small changes more
    evident.

    Upon completetion, it returns the processed image.
    """
    in_min = np.percentile(image, 5)
    in_max = np.percentile(image, 95)

    out_min = 0.0
    out_max = 255.0

    out = image - in_min

    out *= ((out_min-out_max) / (in_min-in_max))
    out += in_min
    return out


def calc_ndvi(image):
    """
    This function takes a pixel value array, `image`, as argument.
    The image is processed according to NDVI calculation model,
    based on the reflectance of red and infrared radiation by healthy
    vegetation.

    The function returns a greyscale image where pixel value is 
    proportional to NDVI, lighter values corresponding to high NDVI
    and darker values to lower NDVI.
    """
    b, g, r = cv2.split(image)
    bottom = (r.astype(float) + b.astype(float))
    bottom[bottom == 0] = 0.01
    ndvi = (b.astype(float)-r) / bottom
    return ndvi


def process(image, show=False, delay=-1):
    """
    This function takes in an array of pixel values, `image`, 
    as argument, a boolean `show` and an integer `delay`.

    The image will be processed, undergoing an increase in contrast,
    NDVI calculation and another increase in contrast.

    If `show` is True, the image will be displayed at each processing
    step, including the original image, for the amount of time (seconds)
    specified by the `delay` argument, in seconds.

    If `delay` assumes a value of -1, the images will be shown until
    input is given by the user.
    """
    if show:
        display(image, 'Original', delay)
    contrasted = contrast_stretch(image)
    if show:
        display(contrasted, 'Contrasted Original', delay)
    ndvi = calc_ndvi(contrasted)
    if show:
        display(ndvi, 'NDVI', delay)
    ndvi_contrasted = contrast_stretch(ndvi)
    if show:
        display(ndvi_contrasted, 'NDVI Contrasted', delay)
    return ndvi_contrasted


def colour_map(image, cm=fastiecm.fastiecm):
    """
    This function takes as argument a pixel value array, `image`, and a
    colour map, defaulting to the fastie colour map.

    It returns the image as colour mapped in accordance to the provided
    colour map.
    """
    color_mapped_prep = image.astype(np.uint8)
    color_mapped_image = cv2.applyColorMap(color_mapped_prep, cm)
    return color_mapped_image


def process_all(base_folder):
    """
    This funcion takes a directory path, `base_folder`, as an argument.
    Looping through every file and folder in the specified directory
    (without recursiveness), for every file with extension '.jpg' or
    '.jpeg', making sure not to process the same image twice or process
    an already NDVI image, it'll be processed into a greyscale NDVI
    image, which is saved in the same directory with a filename of
    the form `{filename}_ndvi.png`, where filename is the name of the
    original image.

    A processed image will then be colour mapped, again, checking if it
    has been colour mapped before, and the resulting image will be written
    to the `base_folder` directory with the filename with the structure
    `{filename}_ndvi_cm.png`, where filename is the name of the original
    unprocessed image.

    This is done continuously and without user input, with the elapsed
    time being calculated and printed to the console upon the
    termination of the loop.
    """

    start_time = datetime.now()
    files = os.listdir(base_folder)
    for image in files:

        if image.endswith(".jpg") or image.endswith(".jpeg"):
            original = cv2.imread(str(base_folder / str(image)))

            filename, extension = image.split(".", 1)
            if filename + "_ndvi.png" not in files:
                print(f"processing {filename}")
                ndvi_contrasted = process(original)
                cv2.imwrite(
                    str(base_folder / str(filename + '_ndvi.png')),
                    ndvi_contrasted)
                cv2.imwrite(str(base_folder / str(filename + '_ndvi_cm.png')),
                            colour_map(ndvi_contrasted))
            elif filename + "_ndvi_cm.png" not in files:
                processed = cv2.imread(
                    str(base_folder / str(filename + "_ndvi.png")))
                cv2.imwrite(str(base_folder / str(filename + '_ndvi_cm.png')),
                            colour_map(processed))
    finish_time = datetime.now()
    elapsed = finish_time - start_time
    print(elapsed)
    minutes, seconds = divmod(elapsed.days * 60*60*24 + elapsed.seconds, 60)
    print(f"{minutes} minutes and {seconds} seconds have passed")
    return minutes, seconds


process_all(Path(__file__).parent.resolve())

# Built with code provided by the Raspberry Pi Foundation, namely that
# present on the following website:
# https://projects.raspberrypi.org/en/projects/astropi-ndvi
# Consulted on 16/02/2023 at   16:04
# Written by team Trivials for the 2022/2023 AstroPi
# Competition - Mission Space Lab.
# Formatted according to the PEP 8 Style Guide standard for Python code.
