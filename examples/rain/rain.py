# -*- coding: utf-8 -*-
import voxbox.util
import voxbox.magicavoxel

import matplotlib.pyplot as plt

import numpy as np

import random

import os

f = open("HDR_L.raw", "rb")
f.seek(4*6, os.SEEK_SET)

blue_noise_data = np.fromfile(f, dtype=np.uint32)
blue_noise_data = blue_noise_data.reshape((64,64,64))

#blue_noise_data[blue_noise_data <= 250000] = 0
#blue_noise_data[blue_noise_data > 250000] = 255
#
#plt.imshow(blue_noise_data[0], cmap="Greys_r", interpolation="nearest")


random.seed(12345)  

drop_count = 10000
drop_length = 3
drop_speed = 3

filename = "C:/Users/David/Downloads/MagicaVoxel-0.98.2-win/MagicaVoxel-0.98.2-win/vox/monu10.vox"
volume_list, palette = voxbox.magicavoxel.read(filename)

model_volume = volume_list[0]

rain_volume = np.zeros(model_volume.shape, dtype=np.uint8)

for col in range(rain_volume.shape[2]):
    for row in range(0,rain_volume.shape[1]):
        for plane in range(0,rain_volume.shape[0]):
            
            if blue_noise_data[plane%64][row%64][col%64] < 1000:
                rain_volume[plane][row][col] = 255

#for drop in range(drop_count):
#    
#    plane = random.randrange(0, model_volume.shape[0])
#    row = random.randrange(0, model_volume.shape[1])
#    col = random.randrange(0, model_volume.shape[2])
#    
#    rain_volume[plane][row][col] = 255
               
plt.imshow(rain_volume[0], cmap="Greys_r", interpolation="nearest")
              
for i in range(drop_length - 1):
    for col in range(model_volume.shape[2]):
        for row in range(0,model_volume.shape[1]):
            for plane in range(0,model_volume.shape[0]):
                if(rain_volume[(plane+1)%model_volume.shape[0]][row][col]) > 0:
                    rain_volume[plane][row][col] = 255

for col in range(model_volume.shape[2]):
        for row in range(model_volume.shape[1]):
            for plane in reversed(range(model_volume.shape[0])):
                
                if(model_volume[plane][row][col]) > 0:
                    break
                
                model_volume[plane][row][col] = rain_volume[plane][row][col]

      
filename = "rain.vox"
voxbox.magicavoxel.write([model_volume], filename, palette)
voxbox.util.open_in_default_app(filename)