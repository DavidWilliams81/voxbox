import struct

import numpy as np

import voxbox.util

def write_chunk(id, chunk_content, child_chunks):
    
    data = bytearray(id)
    
    chunk_content_length = len(chunk_content) if chunk_content else 0
    child_chunks_length = len(child_chunks) if child_chunks else 0
    data = data + struct.pack('ii', chunk_content_length, child_chunks_length)
    
    if chunk_content:
        data = data + chunk_content
        
    if child_chunks:
        data = data + child_chunks
    return data

def write_size_chunk(volume):
    
    chunk_content = struct.pack('iii', len(volume[0][0]), len(volume[0]), len(volume))
    return write_chunk(b'SIZE', chunk_content, None)
    
def write_xyzi_chunk(volume):
    
    values = np.extract(volume, volume)
    (x, y, z) = np.nonzero(volume)
    voxels = np.stack([z.astype(np.uint8), y.astype(np.uint8), x.astype(np.uint8), values])
    voxels = voxels.transpose()
    voxels = voxels.reshape(-1)
    
    chunk_content = struct.pack('i', len(values))
    chunk_content += bytearray(voxels.tobytes())
                    
    return write_chunk(b'XYZI', chunk_content, None)
    
def write_pack_chunk(volume):
    
    chunk_content = struct.pack('i', len(volume))
    return write_chunk(b'PACK', chunk_content, None)
    
def write_rgba_chunk(palette):
    
    chunk_content = bytearray(palette[1:256].tobytes())
    chunk_content += struct.pack('xxxx')    
    return write_chunk(b'RGBA', chunk_content, None) 

def write_main_chunk(volume, palette):
    
    child_chunks  = write_pack_chunk(volume)
    
    if volume.ndim == 3:
        child_chunks += write_size_chunk(volume)
        child_chunks += write_xyzi_chunk(volume)
    
    elif volume.ndim == 4:
        for i in range(0, len(volume)):
            child_chunks += write_size_chunk(volume[i])
            child_chunks += write_xyzi_chunk(volume[i])
    
    if palette is not None:
        child_chunks += write_rgba_chunk(palette)
    
    return write_chunk(b'MAIN', None, child_chunks)
    
def write(volume, filename, palette = None):
    
    data = bytearray(b'VOX ')
    data = data + struct.pack('i', 150);
    data = data + write_main_chunk(volume, palette)
    
    file = open(filename, "wb")
    file.write(data)
    file.close()

if __name__ == "__main__":
    
    palette = np.zeros((256, 4), dtype=np.uint8)
    palette[1] = [255, 0, 0, 255]
    palette[2] = [0, 255, 0, 255]
    palette[3] = [0, 0, 255, 255]
    palette[255] = [255, 255, 255, 255]
    
    row_count = 40
    col_count = 40
    plane_count = 40
    
    voxels = np.zeros((plane_count, col_count, row_count), dtype=np.uint8)
          
    for row in range(0, row_count):
        voxels[0][0][row] = 1; # Red
              
    for col in range(0, col_count):
        voxels[0][col][0] = 2; # Green
              
    for plane in range(0, plane_count):
        voxels[plane][0][0] = 3; #Blue
              
    voxels[0][0][0] = 255 # White
          
    filename = "test_magicavoxel_write.vox"
    write(voxels, filename, palette)
    voxbox.util.open_in_default_app(filename)
    