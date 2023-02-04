import os
from picamera import PiCamera
from time import sleep, perf_counter
from orbit import ISS
from pathlib import Path
from datetime import datetime, timedelta


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

for i in range(3*60-4):
    st = perf_counter()  # start time of the loop
    now_time = datetime.now()
    if now_time >= start_time + timedelta(hours=3):
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
        df.write(
            f"{photo_timestamp}; image_{i:03d}.jpg; {lat}; {northsouth}; {long}; {eastwest} \n")

        # dump the buffer into the file and write it to the disk
        df.flush()
        os.fsync(df.fileno())
    sleep(60)
    et = perf_counter()  # end time of the loop
    print(f"the loop took {et-st:0.2f} seconds to complete")

camera.close()
