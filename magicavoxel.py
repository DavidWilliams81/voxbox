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

    chunk_content = bytearray()
                    
    for (slice, row, col), value in np.ndenumerate(volume):
        if value != 0:
            chunk_content = chunk_content + struct.pack('BBBB', col, row, slice, value)
            
    num_voxels = len(chunk_content) // 4 # 4 bytes per voxel
    chunk_content = struct.pack('i', num_voxels) + chunk_content
                    
    return write_chunk(b'XYZI', chunk_content, bytearray())
    
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