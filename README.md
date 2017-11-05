# voxbox
The Voxel Toolbox (a.k.a 'voxbox') is a Python package for working with voxel data, primarily for making voxel art and video games.

## Features
* Export NumPy array as [MagicaVoxel](https://ephtracy.github.io/) file.

## Installation
Download the code update your $PYTHONPATH environment variable to ensure your Python interpreter can find it. I doubt if I'll get around to making this into a proper package with installer, etc.

## Example
The following snippet shows how to export a NumPy array as a MagicaVoxel file. See [waves.py](examples/waves/waves.py) for the complete code

```python
# Define the size of the volume
row_count = 126
col_count = 126
plane_count = 64

# Create a simple heightmap (could also load something from disk)
heightmap = generate_waves_heightmap(row_count, col_count)

# Create a NumPy array
voxels = np.zeros((plane_count, col_count, row_count), dtype=np.uint8)

# Select a material (white in default palette)
material_index = 1

# For each voxel in the volume
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
                voxels[plane][col][row] = material_index 


# Save the volume to disk as a MagicaVoxel file.
filename = "waves.vox"
voxbox.magicavoxel.write(voxels, filename)
```
    
# Result
The above code generats the following image:
![Screenshot of result](examples/waves/result.png)
