# AstroPi-2023 - Mission SpaceLab

## Objective
Use images captured by the AstroPi SpaceLab mission aboard the ISS to calculate NDVI and with it measure the impact of wildfires on long term foliage density and forest cover and, if possible with the collected imagery, observe differences in vegetation coverage surrounding urban areas and check for its evolution over time as compared with previous NDVI surveys.

## To-Do:
- ~~Sync data written to files to the disk~~
- Check the filters necessary for the pictures to be taken
- Make sure the location of the pictures is being correctly written into the csv data file
- Log the time and date of the photos to the csv data file
- Test the NDVI calculation and plotting code for the right formula and make sure all modules necessary are available on Mission SpaceLab
- Decide whether to integrate the image capture and processing all into the 3 hour mission or do the processing once we get the data
- (Maybe) Integrate both the image capture and processing together and automate it for the 3 hour mission
- Test the final code

## Dependecies
- picamera
- orbit
- pathlib
- os
- time
- numpy
- matplotlib
- glob
- earthpy
