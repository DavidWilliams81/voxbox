# For generating our heightmap
import math
import numpy as np

# For generating our palette
import colorsys

# For saving the result
import voxbox.util
import voxbox.magicavoxel

"""
Generates an animated heightmap from overlapping sine functions.
"""
def generate_waves_heightmap(row_count, col_count, timestep):
    
    freq = 0.1 # Controls spacing between waves.   
    result = np.zeros([col_count, row_count])
    
    # Input timestep is in the range 0.0 to 1.0. Map this to zero to 2*pi and
    # pass through sine function to give a vertical scaling factor which to 
    # 0.0 to 1.0 to -1.0 and back to 0.0.
    vertical_scale = math.sin(timestep * math.pi * 2.0)
    
    # For each pixel in the 2D heightmap
    for col in range(0, col_count):
        for row in range(0, row_count):
            
            # Generate two overlapping sine waves as our base output
            result[col][row] = math.sin(row * freq) * math.sin(col * freq)
            
            # Scale according to the timestep to animate it.
            result[col][row] *= vertical_scale
            
            # Output is in the range -1.0 to 1.0, scale to range 0.0 to 1.0
            result[col][row] += 1.0
            result[col][row] *= 0.5
                  
    return result

def generate_rainbow_colourmap():
    
    # Create an empty palette
    palette = np.zeros((256, 4))

    for index in range(0, 256):    
        
        rgb = colorsys.hsv_to_rgb(index / 255.0, 1.0, 1.0) # Get an RGB value
        palette[index] = np.array(rgb + (1.0,)) # Append 1.0 for alpha   
    
    # Our palette is in the 0.0 to 1.0 floating point range.
    # Convert to 8-bit unsigned integers for MagicaVoxel
    palette *= 255.0
    palette = palette.astype(np.uint8)
        
    return palette
        
# Define the size of the volume
row_count = 126
col_count = 126
plane_count = 64
frame_count = 30

palette = generate_rainbow_colourmap()

# Start with an empty list of volumes
volume_list = []

# Later we will choose a material based on the height (plane) of the voxel
palette_offset_per_plane = (len(palette) - 1.0) / plane_count

# For each voxel in the volume
for frame in range(0, frame_count):
    
    print("Generating frame {} of {}...".format(frame + 1, frame_count))
    
    volume = np.zeros((plane_count, col_count, row_count), dtype=np.uint8)
    
    # Create a simple heightmap (could also load something from disk)
    time_step = frame / frame_count
    heightmap = generate_waves_heightmap(row_count, col_count, time_step)

    for plane in range(0, plane_count):
        for col in range(0, col_count):
            for row in range(0, row_count):
                
                # Get the height from the heightmap, and
                # scale to the height of the volume
                height = heightmap[col, row]
                height *= plane_count
                
                # If the current voxel is below the
                # heightmap then set it to be solid.
                if plane <= height:
                    volume[plane][col][row] = palette_offset_per_plane * plane
                  
    # Add the new frame (volume) to the list
    volume_list.append(volume)
    

# Save the volume to disk as a MagicaVoxel file.
print("Saving results...")
filename = "waves.vox"
voxbox.magicavoxel.write(volume_list, filename, palette)
print("Done.")

# Open the file in the default app, which should be MagicaVoxel. Could instead
# try to run MagicaVoxel directly but then we need to know where it is.
voxbox.util.open_in_default_app(filename)
