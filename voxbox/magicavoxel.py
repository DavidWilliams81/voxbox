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
    
def write_pack_chunk(volume_list):
    
    chunk_content = struct.pack('i', len(volume_list))
    return write_chunk(b'PACK', chunk_content, None)
    
def write_rgba_chunk(palette):
    
    chunk_content = bytearray(palette[1:256].tobytes())
    chunk_content += struct.pack('xxxx')    
    return write_chunk(b'RGBA', chunk_content, None) 

def write_main_chunk(volume_list, palette):
    
    child_chunks  = write_pack_chunk(volume_list)
    for volume in volume_list:
        child_chunks += write_size_chunk(volume)
        child_chunks += write_xyzi_chunk(volume)
    
    if palette is not None:
        child_chunks += write_rgba_chunk(palette)
    
    return write_chunk(b'MAIN', None, child_chunks)
    
# This function expects a *list* of 3D NumPy arrays. If you only
# have one ( a single frame) then create a single element list.
def write(volume_list, filename, palette = None):
    
    if not isinstance(volume_list, list):
        raise TypeError("Argument 'volume_list' should be a list")
        
    if not all(type(volume) is np.ndarray for volume in volume_list):
        raise TypeError("All elements of 'volume_list' must be NumPy arrays")
        
    if not all(volume.ndim == 3 for volume in volume_list):
        raise TypeError("All volumes in 'volume_list' must be 3D")
    
    data = bytearray(b'VOX ')
    data = data + struct.pack('i', 150);
    data = data + write_main_chunk(volume_list, palette)
    
    file = open(filename, "wb")
    file.write(data)
    file.close()
    
def read_chunk(data):
    
    id, data = data[:4], data[4:]
    
    print(id)
    
    (chunk_content_size, child_chunks_size), data = struct.unpack("II", data[:8]), data[8:]
    
    chunk_content = data[0 : chunk_content_size]
    child_chunks = data[chunk_content_size : chunk_content_size + child_chunks_size]
    
    while len(child_chunks) > 0:
    
        child_chunk_size = read_chunk(child_chunks)
        
        child_chunks = child_chunks[child_chunk_size:]
    
    return 4 + 8 + chunk_content_size + child_chunks_size
    
def read_size_chunk(file):

    (col_count, row_count, plane_count) = struct.unpack("III", file.read(12))
    
    print("size", col_count, row_count, plane_count)
    
    return np.zeros((plane_count, row_count, col_count), dtype=np.uint8)
    
def read_xyzi_chunk(file, volume_to_fill):
    
    (voxel_count,) = struct.unpack("I", file.read(4))
    #chunk_content = chunk_content[4:]

    for i in range(voxel_count):
        
        (col, row, plane, index) = struct.unpack("BBBB", file.read(4))        
        volume_to_fill[plane][row][col] = index
                      
def read_rgba_chunk(file):
    
    # MagicaVoxel palette storage seems a little odd. The application allows
    # editing of 255 entries numbered 1-255, but these get saved to disk as
    # entries 0-254 in a 256-element array. The last element (255) appears to
    # be dummy data and might always be zero?
    byte_count = 4 * 256 # 256 entries with 4 bytes each
    palette = np.fromfile(file, dtype=np.uint8, count = byte_count)
    palette = palette.reshape((256, 4))
    palette = np.roll(palette, 1, axis=0)
    return palette
    
def read_pack_chunk(chunk_content):
    
    print("pack")
    
def read_main_chunk(file):
    
    (chunk_content_size, child_chunks_size) = struct.unpack("II", file.read(8))
    
    print(chunk_content_size, child_chunks_size)
    
    palette = None
    volume_list = []
    
    while True:
        
        id=file.read(4)
        if not id: break
            
        (chunk_content_size, child_chunks_size) = struct.unpack("II", file.read(8))
        
        #print(id)
        
        #chunk_content = file.read(chunk_content_size)
        
        if id == b'SIZE':
            volume_list.append(read_size_chunk(file))            
        elif id == b'XYZI':
            read_xyzi_chunk(file, volume_list[-1])
        elif id == b'RGBA':
            palette = read_rgba_chunk(file)
        else:
            file.read(chunk_content_size) # Just consume it
            
    return volume_list, palette
            
        
    
def read(filename):
    
    file = open(filename, "rb")
    
    id = file.read(4)
    (ver,) = struct.unpack("I", file.read(4))
    

    main_chunk_header = file.read(4)
    
    volume_list = read_main_chunk(file)
    
    return volume_list


if __name__ == "__main__":
    
    filename = "horse.vox"
    volume_list, palette = read(filename)

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
    write(volume_list, filename, palette)
    voxbox.util.open_in_default_app(filename)
    