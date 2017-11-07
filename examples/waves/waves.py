# For generating our heightmap
import math
import numpy as np

# For generating our palette
import colorsys

# For saving the result
import voxbox.util
import voxbox.magicavoxel

"""
Generates a heightmap image from the Sinc function. This could be implemented
faster using NumPy functions but it's just an example, and I think the raw
python is clearer.
"""
def generate_waves_heightmap(row_count, col_count):
    
    freq = 0.4 # Controls spacing between waves.
    centre_row = (row_count / 2.0) + 0.5
    centre_col = (col_count / 2.0) + 0.5    
    result = np.zeros([col_count, row_count])
    
    # For each pixel in the 2D heightmap
    for col in range(0, col_count):
        for row in range(0, row_count):
            
            # Find the distance between the centre and the current pixel.
            col_dist = col - centre_col
            row_dist = row - centre_row
            dist = math.sqrt(row_dist * row_dist + col_dist * col_dist)            
            dist *= freq
            
            # Sinc function
            result[col][row] = math.sin(dist) / dist
            
            # Scale to the zero to one range.
            sinc_minima = 0.2122
            result[col][row] += sinc_minima
            result[col][row] /= (1.0 + sinc_minima)
                  
    return result

def generate_rainbow_colourmap():
    
    palette = np.zeros((256, 4), dtype=np.uint8)
    
    for index in range(0, 256):
        
        rgb = colorsys.hsv_to_rgb(index / 255.0, 1.0, 1.0)
        
        palette[index] = [rgb[0] * 255.0, rgb[1] * 255.0, rgb[2] * 255.0, 255]
        
    return palette
        
# Define the size of the volume
row_count = 126
col_count = 126
plane_count = 64

palette = generate_rainbow_colourmap()

# Create a simple heightmap (could also load something from disk)
heightmap = generate_waves_heightmap(row_count, col_count)

# Create a NumPy array
voxels = np.zeros((plane_count, col_count, row_count), dtype=np.uint8)

# Later we will choose a material based on the height (plane) of the voxel
palette_offset_per_plane = (len(palette) - 1.0) / plane_count

# For each voxel in the volume
for plane in range(0, plane_count):
    for col in range(0, col_count):
        for row in range(0, row_count):
            
            # Get the height from the heightmap, and
            # scale to the height of the volume
            height = heightmap[col, row]
            height *= plane_count
            
            # If the current voxel is below the
            # heightmap then set it to be solid.
            if plane <= height:
                voxels[plane][col][row] = palette_offset_per_plane * plane
    

# Save the volume to disk as a MagicaVoxel file.
filename = "waves.vox"
voxbox.magicavoxel.write(voxels, filename, palette)

# Open the file in the default app, which should be MagicaVoxel. Could instead
# try to run MagicaVoxel directly but then we need to know where it is.
voxbox.util.open_in_default_app(filename)
