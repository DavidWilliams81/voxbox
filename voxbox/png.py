import os
import numpy as np

from os import listdir
from skimage import io

def read_frames(path, palette):
    
    images = []
    
    for filename in listdir(path):
        
        if filename.endswith('.png'):
            
            images.append(io.imread(path + filename))
            
    # Should really test that all images are the same size.
    
    col_count = images[0].shape[0]
    row_count = images[0].shape[1]
    plane_count = len(images)
    
    volume = np.zeros((plane_count, row_count, col_count), dtype=np.uint8)
    
    for plane in range(plane_count):
        for row in range(row_count):
            for col in range(col_count):
                pixel = images[plane][row][col]
                
                if(pixel[3] > 0): # Alpha
                    
                    volume[plane][row][col] = 1
                
    return volume
    
    

def write_frames(path, frames, palette):
    
    os.makedirs(path, exist_ok=True)
    
    for frame_idx, frame in enumerate(frames):
        write_frame('{}/frame_{}'.format(path, frame_idx), frame, palette)
    
def write_frame(path, frame, palette):

    os.makedirs(path, exist_ok=True)
    (plane_count, row_count, col_count) = frame.shape
    
    for plane_idx, plane in enumerate(frame):
        
        imdata = bytearray()
        
        # Note, do we need to specify C vs. Fortran order here?
        # https://docs.scipy.org/doc/numpy-1.13.0/reference/arrays.nditer.html
        for mat_idx in np.nditer(plane):
            rgba = palette[mat_idx]
            imdata.extend(rgba)
                
        data = write_png(imdata, col_count, row_count)
        with open("{}/{}.png".format(path, plane_idx), 'wb') as fd:
            fd.write(data)
    

# From https://stackoverflow.com/a/19174800/2337254
def write_png(buf, width, height):
    """ buf: must be bytes or a bytearray in Python3.x,
        a regular string in Python2.x.
    """
    import zlib, struct

    # reverse the vertical line order and add null bytes at the start
    width_byte_4 = width * 4
    raw_data = b''.join(b'\x00' + buf[span:span + width_byte_4]
                        for span in range((height - 1) * width_byte_4, -1, - width_byte_4))

    def png_pack(png_tag, data):
        chunk_head = png_tag + data
        return (struct.pack("!I", len(data)) +
                chunk_head +
                struct.pack("!I", 0xFFFFFFFF & zlib.crc32(chunk_head)))

    return b''.join([
        b'\x89PNG\r\n\x1a\n',
        png_pack(b'IHDR', struct.pack("!2I5B", width, height, 8, 6, 0, 0, 0)),
        png_pack(b'IDAT', zlib.compress(raw_data, 9)),
        png_pack(b'IEND', b'')])
    
import magicavoxel
import voxbox.magicavoxel

palette = magicavoxel.default_palette    

volume = read_frames("C:/code/cubiquity-for-unity3d/Assets/Cubiquity/CubiquitySDK/Windows/x86-64/", palette)

filename = "rain.vox"
voxbox.magicavoxel.write([volume], filename, palette)
voxbox.util.open_in_default_app(filename)