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
