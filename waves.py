import numpy as np
import scipy as sp

import voxbox.magicavoxel
import voxbox.util

def waves(freq, height):
    x,y = np.mgrid[0:row_count, 0:col_count]
    dist = np.hypot(x * freq, y * freq)
    #result = np.sin(dist) / np.sqrt(dist)
    result = sp.special.j0(dist)
    result += 0.4
    result *= (height / 1.4)
    return result

row_count = 126
col_count = 126
plane_count = 64

# See https://goo.gl/AP753K
# See https://goo.gl/W15gma
# See https://goo.gl/AXRypy
#x,y = np.mgrid[0:row_count, 0:col_count]
#height=np.sinc(np.hypot(x / row_count,y / col_count))
#height *= 39

height = waves(0.4, plane_count)

voxels = np.zeros((plane_count, col_count, row_count), dtype=np.uint8)
voxels[0x00][0x1a][0x0a] = 0x4f
 
for plane in range(0, plane_count):
    for col in range(0, col_count):
        for row in range(0, row_count):
            if plane < height[col][row]:
                voxels[plane][col][row] = 0x4f
    

# Save the volume to disk
filename = "waves.vox"
voxbox.magicavoxel.write(voxels, filename)

# Open the file in the default app, which should be MagicaVoxel. Could instead
# try to run MagicaVoxel directly but then we need to know where it is.
voxbox.util.open_in_default_app(filename)