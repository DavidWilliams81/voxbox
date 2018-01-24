import voxbox.geometry
import voxbox.magicavoxel
import voxbox.png

import numpy as np

# Define the size of the volume
col_count = 126
row_count = 126
plane_count = 64

volume = np.zeros((plane_count, row_count, col_count), dtype=np.uint8) 

voxbox.geometry.draw_box(volume, [5,5,5], [60, 120, 120], 216, 249)

voxbox.png.write_frame('temp', volume, voxbox.magicavoxel.default_palette)
