# For generating our heightmap
import math
import numpy as np

import scipy.ndimage.filters

# For saving the result
import voxbox.util
import voxbox.magicavoxel
        
# Define the size of the volume
row_count = 126
col_count = 126
plane_count = 64
frame_count = 2

heightmap = np.zeros((frame_count, row_count, col_count))
    
for i in range(0, 4):
    a = np.random.rand(frame_count, row_count, col_count)
    octave = scipy.ndimage.filters.gaussian_filter(a, math.pow(2.0, i), mode='wrap')    

    octave = octave - octave.min()
    octave = octave / octave.max()
    
    octave *= math.pow(2.0, i)
    
    heightmap += octave
    
heightmap = heightmap - heightmap.min()
heightmap = heightmap / heightmap.max()

heightmap -= 0.5
heightmap *= 0.2
heightmap += 0.5

def checkered_box(volume, lower_corner, upper_corner):
    
    for plane in range(lower_corner[0], upper_corner[0] + 1):
        for col in range(lower_corner[1], upper_corner[1] + 1):
            for row in range(lower_corner[2], upper_corner[2] + 1):
                
                volume[plane][col][row] = 1

# Create a NumPy array
voxels = np.zeros((frame_count, plane_count, col_count, row_count), dtype=np.uint8)

# For each voxel in the volume
for frame in range(0, frame_count):
    
    print("Generating frame {} of {}...".format(frame + 1, frame_count))
    
    checkered_box(voxels[frame], (0, 0, 0), (0, row_count-1, col_count-1))
    
    checkered_box(voxels[frame], (0, 0, 0), (plane_count-25, 0, col_count-1))
    checkered_box(voxels[frame], (0, row_count-1, 0), (plane_count-25, row_count-1, col_count-1))
    
    checkered_box(voxels[frame], (0, 0, 0), (plane_count-25, row_count - 1, 0))
    checkered_box(voxels[frame], (0, 0, col_count - 1), (plane_count-25, row_count - 1, col_count - 1))

    for plane in range(0, plane_count):
        for col in range(0, col_count):
            for row in range(0, row_count):
                
                # Get the height from the heightmap, and
                # scale to the height of the volume
                height = heightmap[frame][col][row]
                height *= plane_count
                
                # If the current voxel is below the
                # heightmap then set it to be solid.
                if plane <= height:
                    
                    # But only if it is currently empty
                    if voxels[frame][plane][col][row] == 0:
                        voxels[frame][plane][col][row] = 79
    

# Save the volume to disk as a MagicaVoxel file.
print("Saving results...")
filename = "waves.vox"
voxbox.magicavoxel.write(voxels, filename)
print("Done.")

# Open the file in the default app, which should be MagicaVoxel. Could instead
# try to run MagicaVoxel directly but then we need to know where it is.
voxbox.util.open_in_default_app(filename)
