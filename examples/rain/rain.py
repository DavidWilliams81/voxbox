# -*- coding: utf-8 -*-
import voxbox.geometry
import voxbox.util
import voxbox.magicavoxel

import matplotlib.pyplot as plt

import numpy as np

import random

import os

import time

import zipfile
blue_noise_zip = zipfile.ZipFile('blue_noise.zip', 'r')
HDR_L_raw = archive.read('HDR_L.raw')

blue_noise_data = np.frombuffer(HDR_L_raw, dtype=np.uint32, offset=4*6)
blue_noise_data = blue_noise_data.reshape((64,64,64))

random.seed(12345)  

frame_count = 30
drop_count = 200
drop_length = 4
drop_speed = 2

load_from_file = False

if load_from_file:
    
    filename = "C:/Users/David/Downloads/MagicaVoxel-0.98.2-win/MagicaVoxel-0.98.2-win/vox/monu10.vox"
    volume_list, palette = voxbox.magicavoxel.read(filename)
    src_volume = volume_list[0]
    
else:
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


rain_volume = np.zeros((frame_count * drop_speed, src_volume.shape[1],src_volume.shape[2]), dtype=np.uint8)

for col in range(rain_volume.shape[2]):
    for row in range(0,rain_volume.shape[1]):
        for plane in range(0,rain_volume.shape[0]):
            
            if blue_noise_data[plane%64][row%64][col%64] < drop_count:
                rain_volume[plane][row][col] = 255
            
for i in range(drop_length - 1):
    for col in range(rain_volume.shape[2]):
        for row in range(0,rain_volume.shape[1]):
            for plane in range(0,rain_volume.shape[0]):
                if(rain_volume[(plane+1)%rain_volume.shape[0]][row][col]) > 0:
                    rain_volume[plane][row][col] = 255
                               
tiles = src_volume.shape[0] // rain_volume.shape[0] + 1
                        
rain_volume = np.tile(rain_volume,(tiles, 1, 1))

model_volumes = []

t0 = time.time()

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
                    if rain_volume[plane][row][col] == 255:
                        model_volume[plane][row][col] = 255
                else:
                    
                    if rain_volume[plane][row][col] == 255:
                        if plane < 120:
                            if row > 0 and row < 125 and col > 0 and col < 125:
                                
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
                    
#                if rain_mask[plane][row][col] == 1:
#                    if rain_volume[plane][row][col] == 255:
#                        if plane > 0:
#                            if row > 0 and row < 125 and col > 0 and col < 125:
#                                model_volume[plane-1][row-1][col-1] = 255
#                                model_volume[plane-1][row-1][col+1] = 255
#                                model_volume[plane-1][row+1][col-1] = 255
#                                model_volume[plane-1][row+1][col+1] = 255
                
    model_volumes.append(model_volume)
    
    rain_volume = np.roll(rain_volume, -drop_speed, axis=0)

t1 = time.time()

print("Done in {}".format(t1-t0))
      
filename = "rain.vox"
voxbox.magicavoxel.write(model_volumes, filename, palette)
voxbox.util.open_in_default_app(filename)