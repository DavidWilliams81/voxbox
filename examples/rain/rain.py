# -*- coding: utf-8 -*-
import os
import zipfile

import numpy as np

import voxbox.geometry
import voxbox.magicavoxel
import voxbox.util

def tile_array_to_size(input_array, output_size):
    
    # x.take(range(0,5),mode='wrap', axis=0).take(range(0,5),mode='wrap',axis=1)
    
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
    
    # Generate s simple sccene for testing purposes.
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
    
# Crop/duplicate vertically as required to ensure that the rain volume will
# tile for the specified number of frames and for the given rain speed.
# The horiozontal dimensions are not changed.

# Make the rain volume have a height such that it will tile vertically for the 
# given rain speed and frame count. The output may be taller or shorter than
# the input depending on these parameters and the size of the initial noisee.
rain_volume = tile_array_to_size(rain_volume, (frame_count * drop_speed, rain_volume.shape[1], rain_volume.shape[2]))

# Elongate the rain drops (with wrapping so the rain volume is tileable)
for i in range(drop_length - 1):    
    rain_volume = np.logical_or(rain_volume, np.roll(rain_volume, 1, axis=0))

# Now make the rain volume the same size as the source volume. This will
# probably involve duplicating it, but could involve cropping for small inputs.
#rain_volume = tile_array_to_size(rain_volume, src_volume.shape)



model_volumes = []

rain_mask = np.zeros(src_volume.shape, dtype=np.bool)

for col in range(src_volume.shape[2]):
    for row in range(src_volume.shape[1]):
        for plane in reversed(range(src_volume.shape[0])):
            
            if(src_volume[plane][row][col]) > 0:
                break
            
            rain_mask[plane][row][col] = True

for frame in range(frame_count):
    
    print("Generating frame {}".format(frame))
    model_volume = np.copy(src_volume)

    
    for col in range(model_volume.shape[2]):
        for row in range(model_volume.shape[1]):
            for plane in reversed(range(model_volume.shape[0])): 
                
                if rain_mask[plane][row][col]:  
                    if rain_volume[plane%60][row%64][col%64]:
                        model_volume[plane][row][col] = 255
                else:
                    
                    if rain_volume[plane%60][row%64][col%64]:
                        if plane < 120:
                            if row > 0 and row < 71 and col > 0 and col < 71:
                                
                                model_volume[plane+1][row-1][col-1] = 255
                                model_volume[plane+1][row-1][col+0] = 255
                                model_volume[plane+1][row-1][col+1] = 255
                                            
                                model_volume[plane+1][row+0][col-1] = 255
                                #model_volume[plane+1][row+0][col+0] = 255
                                model_volume[plane+1][row+0][col+1] = 255
                                            
                                model_volume[plane+1][row+1][col-1] = 255
                                model_volume[plane+1][row+1][col+0] = 255
                                model_volume[plane+1][row+1][col+1] = 255
                    
                    break
                    
                
    model_volumes.append(model_volume)
    
    rain_volume = np.roll(rain_volume, -drop_speed, axis=0)

print("Done")
      
filename = "rain.vox"
voxbox.magicavoxel.write(model_volumes, filename, palette)
voxbox.util.open_in_default_app(filename)