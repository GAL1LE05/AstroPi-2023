import os
from picamera import PiCamera
from time import sleep, perf_counter
from orbit import ISS
from pathlib import Path
from datetime import datetime, timedelta
import csv
from logzero import logfile, logger
import ndvi


def create_csv_file(data_file):
    """Create a new CSV file and add the header row"""
    with open(data_file, 'w') as file:
        writer = csv.writer(file, delimiter=';')
        header = ("Timestamp", "Filename", "Latitude",
                  "North/South", "Longitude", "East/West")
        writer.writerow(header)


def add_csv_data(data_file, data):
    """Add a row of data to the data_file CSV"""
    with open(data_file, 'a') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(data)


def convert(angle):
    """
    Convert a `skyfield` Angle to an EXIF-appropriate
    representation (positive rationals)
    e.g. 98° 34' 58.7 to "98/1,34/1,587/10"

    Return a tuple containing a boolean and the converted angle,
    with the boolean indicating if the angle is negative.
    """
    sign, degrees, minutes, seconds = angle.signed_dms()
    exif_angle = f'{degrees:.0f}/1,{minutes:.0f}/1,{seconds*10:.0f}/10'
    return sign < 0, exif_angle


def capture(camera, image):
    """Use `camera` to capture an `image` file with lat/long EXIF data."""
    point = ISS.coordinates()

    # Convert the latitude and longitude to EXIF-appropriate
    # representations
    south, exif_latitude = convert(point.latitude)
    west, exif_longitude = convert(point.longitude)

    # Set the EXIF tags specifying the current location
    camera.exif_tags['GPS.GPSLatitude'] = exif_latitude
    camera.exif_tags['GPS.GPSLatitudeRef'] = "S" if south else "N"
    camera.exif_tags['GPS.GPSLongitude'] = exif_longitude
    camera.exif_tags['GPS.GPSLongitudeRef'] = "W" if west else "E"

    # Capture the image
    camera.capture(image)


base_folder = Path(__file__).parent.resolve()

# Set up the camera
camera = PiCamera()
camera.resolution = (2591, 1944)

# Get the start time of the script
start_time = datetime.now()
# Get the current time
now_time = datetime.now()
# Set the desired time taken per loop in seconds
loop_time = 50
# Set the total time for the script to run for in minutes
total_time = 10

logfile(str(base_folder / "log.txt"))
logger.info(f"Start Time: {start_time}\n")

img_data_file = base_folder / "image_data.csv"
create_csv_file(img_data_file)

# Loop for the necessary times to get as close to the total time, in
# minutes, as possible, with the expected loop duration.
for i in range(int(total_time*60/loop_time)-1):
    # Get the start time of the loop
    loop_start = perf_counter()
    # Update the current time
    now_time = datetime.now()

    # Check if the total time available or more have passed,
    # and if so, break out of the loop. Serves as a second checkpoint
    # to make sure the code doesn't run for more than 3 hours.
    if now_time >= start_time + timedelta(minutes=total_time-1):
        break
    try:
        # Open the data file in append mode
        with open(img_data_file, 'a') as data_file:
            # Capture a picture and save it with filename of the form
            # `image_xxx.jpg`.
            capture(camera, f'{base_folder}/image_{i:03d}.jpg')

            # Get the coordinates of the ISS and convert them to the
            # desired format.
            point = ISS.coordinates()
            south, lat = convert(point.latitude)
            west, long = convert(point.longitude)
            northsouth = "S" if south else "N"
            eastwest = "W" if west else "E"
            # Get the time at which the photo was taken and format it.
            photo_timestamp = datetime.now().strftime('%d-%m-%Y %H:%M:%S')

            # Save the data relating to the photo
            add_csv_data(
                data_file, (photo_timestamp, f"image_{i:03d}.jpg", lat,
                northsouth, long, eastwest))

            # Write changes to the data file to the disk
            data_file.flush()
            os.fsync(data_file.fileno())
        
        # Process all unprocessed images in the current directory and
        # save the elapsed time to a minutes and seconds pair of
        # variables.
        min, sec = ndvi.process_all(base_folder)

        # Log the time necessary for the processing to be completed to
        # the log file.
        logger.info(
            f"Processing no. {i} took {min} minutes and {sec} seconds to \
            complete\n")
        
        # Check if the desired time for a loop to take has passed.
        # If so, continue. If not, wait for the remaining time.
        if min < 1 and sec < loop_time:
            sleep(loop_time - sec)
        else:
            pass

        # Get the end time of the current loop
        loop_end = perf_counter()

        # Log the time elapsed during the entire loop to the log file,
        # with two decimal places of precision.
        logger.info(f"Cycle took {loop_end - loop_start:0.2f} seconds \
                  to complete\n")
    except Exception as e:
        logger.exception(e)

# Close the camera
camera.close()
# Get the finish time of the script
finish_time = datetime.now()
# Calculate the elapsed time
elapsed = finish_time - start_time
# Divide the elapsed time into minutes and seconds
minutes, seconds = divmod(elapsed.days * 60*60*24 + elapsed.seconds, 60)
# Log the finish time and total elapsed time to the log file
logger.info(f"End Time: {finish_time}\n")
logger.info(f"Total time: {minutes} min {seconds} s\n")


# Built with code provided by the Raspberry Pi Foundation, namely that
# present on the following website:
# https://projects.raspberrypi.org/en/projects/code-for-your-astro-pi-mission-space-lab-experiment
# Written by team Trivials for the 2022/2023 AstroPi
# Competition - Mission Space Lab.
# Formatted according to the PEP 8 Style Guide standard for Python code.
