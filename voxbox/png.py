import os

def write_volume_list(path, volume_list, palette):
    
    os.makedirs(path, exist_ok=True)
    
    for volume in range(0, len(volume_list)):
        write_volume('{}/frame_{}'.format(path, volume), volume_list[volume], palette)
    
def write_volume(path, volume, palette):

    os.makedirs(path, exist_ok=True)
    (plane_count, row_count, col_count) = volume.shape
    
    for plane in range(0, plane_count):
        
        imdata = bytearray()
        for row in range(0, row_count):
            for col in range(0, col_count):
                mat = volume[plane][row][col]
                rgba = palette[mat]
                #print(rgba)
                imdata.append(rgba[0])
                imdata.append(rgba[1])
                imdata.append(rgba[2])
                imdata.append(rgba[3])
                
        data = write_png(imdata, col_count, row_count)
        with open("{}/{}.png".format(path, plane), 'wb') as fd:
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