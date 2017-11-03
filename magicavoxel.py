import struct

import numpy as np

def write_chunk(id, chunk_content, child_chunks):
    
    data = bytearray(id)
    data = data + struct.pack('ii', len(chunk_content), len(child_chunks))
    data = data + chunk_content
    data = data + child_chunks
    return data

def write_size_chunk(volume):
    
    chunk_content = struct.pack('iii', len(volume[0][0]), len(volume[0]), len(volume))
    return write_chunk(b'SIZE', chunk_content, bytearray())
    
def write_xyzi_chunk(volume):
    
    values = np.extract(volume, volume)
    (x, y, z) = np.nonzero(volume)
    voxels = np.stack([z.astype(np.uint8), y.astype(np.uint8), x.astype(np.uint8), values])
    voxels = voxels.transpose()
    voxels = voxels.reshape(-1)
    
    chunk_content = struct.pack('i', len(values))
    chunk_content += bytearray(voxels.tobytes())
                    
    return write_chunk(b'XYZI', chunk_content, bytearray())
    
def write_pack_chunk(volume):
    
    chunk_content = struct.pack('i', 1) # 1 model for now    
    return write_chunk(b'PACK', chunk_content, bytearray())


def write_main_chunk(volume):

    pack_chunk_data = write_pack_chunk(volume)
    size_chunk_data = write_size_chunk(volume)
    xyzi_chunk_data = write_xyzi_chunk(volume)
    children_chunk_size = len(pack_chunk_data) + len(size_chunk_data) + len(xyzi_chunk_data)

    chunk_size = 0;    
    data = bytearray(b'MAIN')
    data = data + struct.pack('ii', chunk_size, children_chunk_size)
    data = data + pack_chunk_data
    data = data + size_chunk_data
    data = data + xyzi_chunk_data
    
    return data
    
def write_magicavoxel(volume):
    
    data = bytearray(b'VOX ')
    data = data + struct.pack('i', 150);
    data = data + write_main_chunk(volume)
    return data

import numpy as np
import scipy as sp

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
slice_count = 64

# See https://goo.gl/AP753K
# See https://goo.gl/W15gma
# See https://goo.gl/AXRypy
#x,y = np.mgrid[0:row_count, 0:col_count]
#height=np.sinc(np.hypot(x / row_count,y / col_count))
#height *= 39

height = waves(0.4, slice_count)

v = np.zeros((slice_count, col_count, row_count), dtype=np.uint8)
v[0x00][0x1a][0x0a] = 0x4f
 
for slice in range(0, slice_count):
    for col in range(0, col_count):
        for row in range(0, row_count):
            if slice < height[col][row]:
                v[slice][col][row] = 0x4f
    
    
result = write_magicavoxel(v)


#data = bytearray(b'TEST')
#write_main_chunk(data)
#
file = open("filename.vox", "wb")
file.write(result)
file.close()