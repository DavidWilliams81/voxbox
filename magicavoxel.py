#import random
import struct

import numpy as np

#floatlist = [random.random() for _ in range(10)]
#buf = struct.pack('%sf' % len(floatlist), *floatlist)

def write_size_chunk(volume):
    
    data = bytearray(b'SIZE')
    data = data + struct.pack('ii', 12, 0) # Size of chunk and children
    data = data + struct.pack('iii', len(volume[0][0]), len(volume[0]), len(volume)) # Size of volume
    return data
    
def write_xyzi_chunk(volume):
    
    slice_count = len(volume)
    row_count = len(volume[0])
    col_count = len(volume[0][0])

    voxels = []
    
    for s in range(0, slice_count):
        for r in range(0, row_count):
            for c in range(0, col_count):
                
                voxel = volume[s][r][c]
                if voxel != 0:
                    voxels.append((c, r, s, voxel))
                    
    chunk_content = struct.pack('i', len(voxels))
    for voxel in voxels:        
        chunk_content = chunk_content + struct.pack('BBBB', voxel[0], voxel[1], voxel[2], voxel[3])
        
    data = bytearray(b'XYZI')
    data = data + struct.pack('ii', len(chunk_content), 0)
    data = data + chunk_content
    return data
    
    #data = bytearray(b'XYZI')
    #data = data + struct.pack('ii', 12, 0) # Size of chunk and children
    #data = data + struct.pack('iii', 0x28, 0x28, 0x28) # Size of volume
    
def write_pack_chunk(volume):
  
    data = bytearray(b'PACK')
    data = data + struct.pack('ii', 4, 0) # 4 bytes to specify number of models
    data = data + struct.pack('i', 1) # 1 model for now    
    return data

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

v = np.zeros((0x28, 0x28, 0x28), dtype=np.uint8)
v[0x00][0x1a][0x0a] = 0x4f
    
result = write_magicavoxel(v)


#data = bytearray(b'TEST')
#write_main_chunk(data)
#
file = open("filename.vox", "wb")
file.write(result)
file.close()