# For generating our heightmap
import math
import numpy as np
import scipy.ndimage.filters

# For creating and saving our frames
import voxbox.geometry
import voxbox.magicavoxel
import voxbox.util
        
# Define the size of the volume
row_count = 126
col_count = 126
plane_count = 64
frame_count = 30

# A 3D array, which can also be considered as a 1D array of 2D heightmap data.
# Each 2D slice will be the heightmap corresponding to a single frame.
# It starts off with zeros and the octaves get added in one at a time.
heightmaps = np.zeros((frame_count, row_count, col_count))

noise_layer_count = 4 # The number of layers of noise we will combine
for layer_index in range(0, noise_layer_count):
    
    # Each layer starts off as random noise.
    layers = np.random.rand(frame_count, row_count, col_count)
    
    # These sigma values control the amount of bluring in each axis. The 
    # pow(2.0, ...) part means that each layer has twice the sigma of the
    # previous one and so is twice as blurred. Note that we have less blurring 
    # in the inter-frame dimension - empirically this was found to look nicer.
    inter_pixel_sigma = math.pow(2.0, layer_index)
    inter_frame_sigma = math.pow(2.0, max(0, layer_index-1))
    layers = scipy.ndimage.filters.gaussian_filter(layers,
                                                  (inter_frame_sigma,
                                                   inter_pixel_sigma,
                                                   inter_pixel_sigma),
                                                  mode='wrap')    

    # Normalise values to lie between zero and one.
    layers = layers - layers.min()
    layers = layers / layers.max()
    
    # Scale the values so that layers which have been blurred less
    # (high-frequency details) contribute less to the overall heightmap.
    layers *= math.pow(2.0, layer_index)
    
    # Combine the layer
    heightmaps += layers
    
# Normalise the heightmaps to between zero and one.
heightmaps = heightmaps - heightmaps.min()
heightmaps = heightmaps / heightmaps.max()

# Bring the range of heights to 0.4 to 0.6. This means the troughs of the waves
# will end up at 40% of the volume height with peaks at 60% of the height.
heightmaps -= 0.5
heightmaps *= 0.2
heightmaps += 0.5

# Now that we have our heightmaps we are ready to start 
# building our scene. Start with an empty list of frames.
frame_list = []

# Materials in MagicaVoxel default palette.
empty_material_index = 0
light_blue_material_index = 151

# For each voxel in the volume
for frame in range(0, frame_count):
    
    print("Generating frame {} of {}...".format(frame + 1, frame_count))
    
    # Each frame is a 3D volume which starts off empty
    volume = np.zeros((plane_count, row_count, col_count), dtype=np.uint8)
    
    # Draw the walls and tower in the middle. This part isn't importand
    # for understanding how the water works. You could instead load 
    # in an existing MagicaVoxel scene and add water to that.
    voxbox.geometry.draw_box(volume, (0, 0, 0), (0, row_count-1, col_count-1), 246, 252)    
    voxbox.geometry.draw_box(volume, (0, 0, 0), (plane_count-25, 0, col_count-1), 246, 252)
    voxbox.geometry.draw_box(volume, (0, row_count-1, 0), (plane_count-25, row_count-1, col_count-1), 246, 252)    
    voxbox.geometry.draw_box(volume, (0, 0, 0), (plane_count-25, row_count - 1, 0), 246, 252)
    voxbox.geometry.draw_box(volume, (0, 0, col_count - 1), (plane_count-25, row_count - 1, col_count - 1), 246, 252)    
    voxbox.geometry.draw_box(volume, (0, 50, 50), (plane_count - 1, 76, 76), 246, 217)

    # Iterate over each voxel and check if it is below the level
    # defined by the heightmap. If so it represents water.
    for plane in range(0, plane_count):
        for row in range(0, row_count):
            for col in range(0, col_count):
                
                # Get the height from the heightmap, and
                # scale to the height of the volume
                height = heightmaps[frame][row][col]
                height *= plane_count
                
                # If the current voxel is below the
                # heightmap then set it to be solid.
                if plane <= height:
                    
                    # But only if it is currently empty
                    if volume[plane][row][col] == empty_material_index:
                        volume[plane][row][col] = light_blue_material_index

    # Add the new frame (volume) to the list
    frame_list.append(volume)
    

# Save the volume to disk as a MagicaVoxel file.
print("Saving results...")
filename = "water.vox"
voxbox.magicavoxel.write(frame_list, filename)
print("Done.")

# Open the file in the default app, which should be MagicaVoxel. Could instead
# try to run MagicaVoxel directly but then we need to know where it is.
voxbox.util.open_in_default_app(filename)
