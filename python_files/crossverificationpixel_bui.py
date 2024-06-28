import os
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from pyproj import Transformer
def calculate_bu(image_path, method, output_path):
    with rasterio.open(image_path) as src:
        # Read the required spectral bands
        band_red = src.read(4).astype('float32') / 10000
        band_green = src.read(3).astype('float32') / 10000
        band_blue = src.read(2).astype('float32') / 10000
        band_nir = src.read(8).astype('float32') / 10000
        band_swir = src.read(11).astype('float32') / 10000
        band_swir2 = src.read(12).astype('float32') / 10000
        
        # Avoid division by zero by adding a small constant (epsilon)
        epsilon = np.finfo(float).eps

        # Calculate the Built-Up Index (BU) based on the specified method
        if method == 'NDBI':
            bu = (band_swir - band_nir) / (band_swir + band_nir + epsilon)
        elif method == 'NBAI':
            bu = (band_swir2 - band_swir) / (band_green + epsilon)
        elif method == 'NBI':
            bu = (band_red * band_swir2) / (band_nir + epsilon)
        elif method == 'MBI':
            bu = ((band_swir * band_red) - (band_nir * band_nir)) / (band_red + band_nir + band_swir + epsilon)
        elif method == 'UI':
            bu = (band_swir - band_nir) / (band_swir + band_nir + epsilon)
        elif method == 'BAEI':
            bu = (band_red + 0.3) / (band_green + band_swir + epsilon)
        elif method == 'BRBA':
            bu = band_red / (band_swir2 + epsilon)
        elif method == 'new_BUI':
            bu = ((band_red + band_green) - (band_blue + band_nir)) / ((band_red + band_green) + (band_blue + band_nir) + epsilon)
        else:
            print("Invalid method specified.")
            return None
        
        # Copy metadata from the source raster
        meta = src.meta
        
        # Update metadata to reflect the number of layers and data type
        meta.update(count=1, dtype='float32')
        
        # Write the BU to the output path
        with rasterio.open(output_path, 'w', **meta) as dst:
            dst.write(bu, 1)
        
        return bu

def layer_stack(input_dir, output_path):
    # Get list of all files in the input directory
    bu_images = []
    for file in os.listdir(input_dir):
        if file.endswith('.tif'):
            bu_images.append(rasterio.open(os.path.join(input_dir, file)))
    
    # Use metadata from the first image
    meta = bu_images[0].meta
    meta.update(count=len(bu_images))
    
    # Write the layer stack to the output path
    with rasterio.open(output_path, 'w', **meta) as dst:
        for idx, bu_image in enumerate(bu_images, start=1):
            dst.write(bu_image.read(1), idx)

# Paths to the input GeoTIFF files
image1_path = 'S2A_MSIL1C_20240214T100121_N0510_R122_T33TTG_20240214T104957_bilinear_rome.tif'
image2_path = 'S2A_MSIL1C_20230818T100031_N0509_R122_T33TTG_20230818T121434_bilinear_rome.tif'

# List of methods for BU calculation
methods = ['NDBI', 'NBAI', 'NBI', 'MBI', 'UI', 'BAEI', 'BRBA', 'new_BUI']

# Output directory for the individual BU images
output_dir1 = './output_image1/'
output_dir2 = './output_image2/'

# Create output directories if they don't exist
os.makedirs(output_dir1, exist_ok=True)
os.makedirs(output_dir2, exist_ok=True)

# Calculate and save BU images for each method in image1_path
for method in methods:
    output1_path = os.path.join(output_dir1, f'{method}.tif')
    calculate_bu(image1_path, method, output1_path)

# Calculate and save BU images for each method in image2_path
for method in methods:
    output2_path = os.path.join(output_dir2, f'{method}.tif')
    calculate_bu(image2_path, method, output2_path)

# Output paths for the layer stacked images
output_layerstack1_path = 'layerstacked_bu_image1.tif'
output_layerstack2_path = 'layerstacked_bu_image2.tif'

# Stack BU images into a layer stack for image1_path
layer_stack(output_dir1, output_layerstack1_path)

# Stack BU images into a layer stack for image2_path
layer_stack(output_dir2, output_layerstack2_path)

print("Layer stacking completed.")



def get_pixel_values_from_coordinates(layerstack_path, coordinates):
    pixel_values = []
    
    with rasterio.open(layerstack_path) as src:
        transformer = Transformer.from_crs("EPSG:4326", src.crs, always_xy=True)
        
        for lat, lon in coordinates:
            x, y = transformer.transform(lon, lat)
            row, col = src.index(x, y)
            
            values_at_coordinates = []
            for layer_idx in range(1, src.count + 1):
                pixel_value = src.read(layer_idx)[row, col]
                values_at_coordinates.append(pixel_value)
            
            pixel_values.append(values_at_coordinates)
    
    return pixel_values
name=None
def plot_pixel_values(pixel_values, coordinates,name):
    num_coordinates = len(coordinates)
    num_layers = len(pixel_values[0])  # Assuming all rows have the same number of layers
    
    plt.figure(figsize=(14, 7))
    
    for coord_idx in range(num_coordinates):
        plt.plot(range(1, num_layers + 1), pixel_values[coord_idx], marker='o', label=f'Coord {coord_idx + 1}')
    
    plt.title(f'Pixel Values at Specific Coordinates - {name}')
    plt.xlabel('Layer Index')
    plt.ylabel('Pixel Value')
   # plt.xticks(range(1, num_layers + 1))
    plt.xticks(range(1, len(methods) + 1), methods, rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

# Paths to the layer stacked images
layerstack1_path = 'layerstacked_bu_image1.tif'
layerstack2_path = 'layerstacked_bu_image2.tif'

# List of geographic coordinates (latitude, longitude) pairs
coordinates = [
    (41.91638085797895, 12.423027274073522),
    (41.91657450073516, 12.42212071335914),
    (41.9156903193817, 12.422270917060224),
    (41.91588392221169, 12.42282881653152),
    (41.915129466623036, 12.422295056939985),
    (41.914959812684955, 12.424164556610625),
    (41.915171381055956, 12.424864613158745),
    (41.91573822115919, 12.401223623062545),
    (41.90583775468933, 12.401352369094383),
    (41.91765426311034, 12.430534802977597),
]

# Get pixel values at specified coordinates from each layer stack image
pixel_values_image1 = get_pixel_values_from_coordinates(layerstack1_path, coordinates)
pixel_values_image2 = get_pixel_values_from_coordinates(layerstack2_path, coordinates)

# Plotting pixel values for each coordinate
plot_pixel_values(pixel_values_image1, coordinates,name="Image1")
plot_pixel_values(pixel_values_image2, coordinates,name="Image2")

