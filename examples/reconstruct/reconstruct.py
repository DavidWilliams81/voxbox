import numpy as np

# For loading the views
from skimage import io

# For saving the result
import voxbox.util
import voxbox.magicavoxel

print("Warning - this example is a failed experiment! See the readme for details.")

front_image = io.imread("doom-marine-silhouette-front.png")
front_image = np.flipud(front_image)
front_image = np.fliplr(front_image)

left_image = io.imread("doom-marine-silhouette-left.png")
left_image = np.flipud(left_image)

if front_image.shape[0] != left_image.shape[0]:
    print("Error - Mismatched shapes!")

plane_count = front_image.shape[0]
row_count = front_image.shape[1]
col_count = left_image.shape[1]

volume = np.zeros((plane_count, row_count, col_count), dtype=np.uint8)

for plane in range(0, plane_count):
    for row in range(0, row_count):
        for col in range(0, col_count):
            
            if front_image[plane, row, 0] > 0:
                if left_image[plane, col, 0] > 0:
                    volume[plane, row, col] = 12
                      
filename = "output.vox"
voxbox.magicavoxel.write([volume], filename)
voxbox.util.open_in_default_app(filename)