import os
from picamera import PiCamera
from time import sleep, perf_counter
from orbit import ISS
from pathlib import Path
from datetime import datetime, timedelta
import csv
import ndvi


def create_csv_file(data_file):
    """Create a new CSV file and add the header row"""
    with open(data_file, 'w') as f:
        writer = csv.writer(f, delimiter=';')
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

    # Convert the latitude and longitude to EXIF-appropriate representations
    south, exif_latitude = convert(point.latitude)
    west, exif_longitude = convert(point.longitude)

    # Set the EXIF tags specifying the current location
    camera.exif_tags['GPS.GPSLatitude'] = exif_latitude
    camera.exif_tags['GPS.GPSLatitudeRef'] = "S" if south else "N"
    camera.exif_tags['GPS.GPSLongitude'] = exif_longitude
    camera.exif_tags['GPS.GPSLongitudeRef'] = "W" if west else "E"

    # Capture the image
    camera.capture(image)


camera = PiCamera()
camera.resolution = (2591, 1944)
base_folder = Path(__file__).parent.resolve()
img_data_file = base_folder / "image_data.csv"

start_time = datetime.now()
now_time = datetime.now()
loop_time = 50
total_time = 10

t = open(str(base_folder / "log.txt"), 'a')
t.write(f"Start Time: {start_time}\n")

create_csv_file(img_data_file)

for i in range(int(total_time*60/loop_time)):
    st = perf_counter()  # start time of the loop
    now_time = datetime.now()
    if now_time >= start_time + timedelta(minutes=179):
        break
    with open(img_data_file, 'a') as df:
        # outputs image with filename image_xxx.jpg
        capture(camera, f'{base_folder}/image_{i:03d}.jpg')

        # gets the coordiates of the ISS and writes it to a data file along with the image filename
        point = ISS.coordinates()
        south, lat = convert(point.latitude)
        west, long = convert(point.longitude)
        northsouth = "S" if south else "N"
        eastwest = "W" if west else "E"
        photo_timestamp = datetime.now().strftime('%d-%m-%Y %H:%M:%S')

        add_csv_data(
            df, f"{photo_timestamp}; image_{i:03d}.jpg; {lat}; {northsouth}; {long}; {eastwest} \n")

        # dump the buffer into the file and write it to the disk
        df.flush()
        os.fsync(df.fileno())
    min, sec = ndvi.process_all(base_folder)
    t.write(
        f"Processing no. {i} took {min} minutes and {sec} seconds to complete\n")
    if min < 1 and sec < loop_time:
        sleep(loop_time - sec)
    else:
        pass
    et = perf_counter()  # end time of the loop
    t.write(f"Cycle took {et-st:0.2f} seconds to complete\n")
    t.flush
    os.fsync(t.fileno())

camera.close()
finish_time = datetime.now()
elapsed = finish_time - start_time
print(elapsed)
minutes, seconds = divmod(elapsed.days * 60*60*24 + elapsed.seconds, 60)
t.write(f"End Time: {finish_time}\n")
print(f"{minutes} minutes and {seconds} seconds have passed")
t.write(f"Total time: {minutes} min {seconds} s\n")
t.flush
os.fsync(t.fileno())
t.close()


# Built with code provided by the Raspberry Pi Foundation, namely that present on the following website:
# https://projects.raspberrypi.org/en/projects/code-for-your-astro-pi-mission-space-lab-experiment
# Formatted in accordance to the pep8 standard
