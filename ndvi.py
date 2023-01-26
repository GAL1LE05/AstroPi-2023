import numpy as np
from PIL import Image

# Open the image
img = Image.open("test_image98.jpeg")

# Convert the image to a numpy array
img_data = np.array(img)

# Extract the red and NIR channels
red = img_data[:,:,0]
nir = img_data[:,:,2]

# Calculate NDVI
ndvi = (nir - red) / (nir + red)

# Save the NDVI image
im = Image.fromarray(ndvi)
im.save("ndvi.jpg")
