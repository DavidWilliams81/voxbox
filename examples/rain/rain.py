# -*- coding: utf-8 -*-
import os
import zipfile

import numpy as np

import voxbox.geometry
import voxbox.magicavoxel
import voxbox.util

def tile_array_to_size(input_array, output_size):
    
    # Find how many times we need to tile out input to
    # be *at least* as big as the desired output size.
    tile_counts = np.floor_divide(output_size, input_array.shape) + 1
    
    # Perform the tiling
    tiled_array = np.tile(input_array ,tile_counts)
    
    # Result is probably larger than required, so crop to desired size.
    return tiled_array[ : output_size[0], : output_size[1], : output_size[2]]

# Properties defining our rain effect.
rain_density = 500 # Higher values mean more rain
drop_length = 4 # In voxels
drop_speed = 2 # In voxels moved per frame
frame_count = 30 # Number of frames

# Load 3D Blue Noise texture (see http://momentsingraphics.de/?p=148)
blue_noise_zip = zipfile.ZipFile('blue_noise.zip', 'r')
HDR_L_raw = blue_noise_zip.read('HDR_L.raw')
blue_noise_start = 6*4 # Skip header of 6 ints
blue_noise_data = np.frombuffer(HDR_L_raw, dtype=np.uint32, offset=blue_noise_start)
blue_noise_data = blue_noise_data.reshape((64,64,64)) # Used texture has known size.

# Create a 3D scene to which we will add the rain effect.
load_from_file = False
if load_from_file:
    
    # Load a scene from disk
    filename = "/path/to/scene.vox"
    volume_list, palette = voxbox.magicavoxel.read(filename)
    src_volume = volume_list[0]
    
else:
    
    # Generate s simple scene for testing purposes.
    src_volume = np.zeros((126, 126, 126), dtype=np.uint8) 
    
    # Floor
    voxbox.geometry.draw_box(src_volume, [0,0,0], [0, 125, 125], 246, 252)
    
    # Pillars
    voxbox.geometry.draw_box(src_volume, [0,60,4], [63, 67, 11], 246, 204)
    voxbox.geometry.draw_box(src_volume, [0,60,116], [63, 67, 123], 246, 204)
    
    voxbox.geometry.draw_box(src_volume, [0,4,60], [63, 11, 67], 246, 204)
    voxbox.geometry.draw_box(src_volume, [0,116,60], [63, 123, 67], 246, 204)
    
    # Bridges
    voxbox.geometry.draw_box(src_volume, [64,50,0], [64, 75, 125], 246, 217)
    voxbox.geometry.draw_box(src_volume, [64,0,50], [64, 125, 75], 246, 217)
    
    palette = voxbox.magicavoxel.default_palette


# Initialise with thresholded version of blue noise
rain_volume = np.less(blue_noise_data, rain_density)

# Make the rain volume have a height such that it will tile vertically for the 
# given rain speed and frame count. The output may be taller or shorter than
# the input depending on these parameters and the size of the initial noisee.
rain_volume = tile_array_to_size(rain_volume, (frame_count * drop_speed, rain_volume.shape[1], rain_volume.shape[2]))

# Elongate the rain drops (with wrapping so the rain volume is tileable)
for i in range(drop_length - 1):    
    rain_volume = np.logical_or(rain_volume, np.roll(rain_volume, 1, axis=0))
               
# Indicates empty voxels in the scene (where rain can potentially be drawn)
rain_mask = np.equal(src_volume, 0)

# The output frames we build
output_volumes = []

rain_material = 255

for frame in range(frame_count):
    
    print("Generating frame {}".format(frame))
    
    # Copy source to output
    output_volume = np.copy(src_volume)
    
    # Note: The code below is not well optimised. I'm sure we could make it
    # faster by using various built-in NumPy functions to tile/broadcast the
    # rain array, mask it, etc. Also the rain_mask could probably be
    # calculated so as to mask out voxels below the surface, as well as the
    # surface itself. But the code is good enough for now.

    # Iterate over each column of the output scene
    for col in range(output_volume.shape[2]):
        for row in range(output_volume.shape[1]):
            
            # Start at the top of the column and work down (so that
            # we can stop if we hit a solid voxel that blocks rain)
            for plane in reversed(range(output_volume.shape[0])): 
                
                # Wrap rain volume
                rain_volume_plane = plane % rain_volume.shape[0]
                rain_volume_row = row % rain_volume.shape[1]
                rain_volume_col = col % rain_volume.shape[2]
                
                # If we have an empty space where we can draw rain...
                if rain_mask[plane][row][col]:
                    # Check if there is rain to draw
                    if rain_volume[rain_volume_plane][rain_volume_row][rain_volume_col]:
                        # Draw the rain voxel
                        output_volume[plane][row][col] = rain_material
                                    
                # If we have reached a surface...
                else:
                    
                    # Check if thre is a rain drop hitting that surface
                    if rain_volume[rain_volume_plane][rain_volume_row][rain_volume_col]:
                        
                        # Avoid writing splashes outside the scene.
                        if (plane < output_volume.shape[0] - 1 and
                            row > 0 and row < output_volume.shape[1] - 1 and
                            col > 0 and col < output_volume.shape[2] - 1):
                                
                            # Draw the splash into surrounding voxels.
                            output_volume[plane+1][row-1][col-1] = rain_material
                            output_volume[plane+1][row-1][col+0] = rain_material
                            output_volume[plane+1][row-1][col+1] = rain_material
                                        
                            output_volume[plane+1][row+0][col-1] = rain_material
                            #output_volume[plane+1][row+0][col+0] = rain_material
                            output_volume[plane+1][row+0][col+1] = rain_material
                                        
                            output_volume[plane+1][row+1][col-1] = rain_material
                            output_volume[plane+1][row+1][col+0] = rain_material
                            output_volume[plane+1][row+1][col+1] = rain_material
                    
                    # Have hit a surface so we can stop processing this column
                    break                    
                
    output_volumes.append(output_volume)
    
    rain_volume = np.roll(rain_volume, -drop_speed, axis=0)

print("Done")
      
filename = "rain.vox"
voxbox.magicavoxel.write(output_volumes, filename, palette)
voxbox.util.open_in_default_app(filename)