# -*- coding: utf-8 -*-
import os
import zipfile

import numpy as np

import voxbox.geometry
import voxbox.magicavoxel
import voxbox.util

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

# Elongate the rain drops
for i in range(drop_length - 1):    
    rain_volume = np.logical_or(rain_volume, np.roll(rain_volume, 1, axis=0))

tiles = np.floor_divide(src_volume.shape, rain_volume.shape) + 1
                        
rain_volume = np.tile(rain_volume,(1, tiles[1], tiles[2]))

rain_volume = rain_volume[:frame_count * drop_speed,:,:]

tiles = np.floor_divide(src_volume.shape, rain_volume.shape) + 1

rain_volume = np.tile(rain_volume,(tiles[0], 1, 1))

# Fill the rain volume by thresholding the 
#for col in range(rain_volume.shape[2]):
#    for row in range(0,rain_volume.shape[1]):
#        for plane in range(0,rain_volume.shape[0]):
#            
#            if blue_noise_data[plane%64][row%64][col%64] < drop_count:
#                rain_volume[plane][row][col] = True
#            
#for i in range(drop_length - 1):
#    for col in range(rain_volume.shape[2]):
#        for row in range(0,rain_volume.shape[1]):
#            for plane in range(0,rain_volume.shape[0]):
#                if(rain_volume[(plane+1)%rain_volume.shape[0]][row][col]):
#                    rain_volume[plane][row][col] = True
#                               
#tiles = src_volume.shape[0] // rain_volume.shape[0] + 1
#                        
#rain_volume = np.tile(rain_volume,(tiles, 1, 1))

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
                    if rain_volume[plane][row][col]:
                        model_volume[plane][row][col] = 255
                else:
                    
                    if rain_volume[plane][row][col]:
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