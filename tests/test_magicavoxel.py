# -*- coding: utf-8 -*-
import voxbox.util
import voxbox.magicavoxel

filename = "horse.vox"
volume_list, palette = voxbox.magicavoxel.read(filename)

palette[1]   = [255, 0,   0,   255] # Red
palette[2]   = [0,   255, 0,   255] # Green
palette[3]   = [0,   0,   255, 255] # Blue
palette[255] = [255, 255, 255, 255] # White

frame_count = len(volume_list)

for frame_index, voxels in enumerate(volume_list):
    
    (plane_count, row_count, col_count) = voxels.shape
          
    for col in range(frame_index, col_count, frame_count):
        voxels[0][0][col] = 1 # Red
        
    for row in range(frame_index, row_count, frame_count):
        voxels[0][row][0] = 2 # Green
              
    for plane in range(frame_index, plane_count, frame_count):
        voxels[plane][0][0] = 3 #Blue
              
    voxels[0][0][0] = 255 # White
      
filename = "test_magicavoxel_write.vox"
voxbox.magicavoxel.write(volume_list, filename, palette)
voxbox.util.open_in_default_app(filename)