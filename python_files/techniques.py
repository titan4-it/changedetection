import rasterio
import numpy as np

def calculate_bu(image_path, output_path, method):
    with rasterio.open(image_path) as src:
        # Read the required spectral bands
        band_red = src.read(4).astype('float32')
        band_green = src.read(3).astype('float32')
        band_blue = src.read(2).astype('float32')
        band_nir = src.read(8).astype('float32')
        band_swir = src.read(11).astype('float32')

        # Avoid division by zero by adding a small constant (epsilon)
        epsilon = np.finfo(float).eps

        # Calculate the Built-Up Index (BU) based on the specified method
        if method == 'NDBI':
            # Normalized Difference Built-up Index (NDBI)
            bu = (band_swir2 - band_nir) / (band_swir2 + band_nir )
       
        elif method == 'MBUI':
            # Modified Built-up Index (MBUI)
            bu = (2 * (band_swir - band_nir) - (band_green - band_red)) / (2 * (band_swir - band_nir) + (band_green - band_red) + epsilon)

        elif method == 'NBAI':
            # Built-Up Area Index (BUAI)
            bu = (band_swir2 - band_swir)/ band_green 
 
        elif method == 'NBI':
            # Simple Ratio (SR)
            bu = (band_red * band_swir2) / (band_nir )

        elif method == 'MBI':
            # Enhanced Built-Up Index (EBUI)
            bu = ((band_swir * band_red) - (band_nir * band_nir)) / (band_red + band_nir + band_swir)

        elif method == 'UI':
            # Urban Index (UI)
            bu = (band_swir - band_nir)/(band_swir + band_nir)
            
        elif method == 'BAEI':
                
            bu = (band_red + 0.3) / (band_green + band_swir)

        elif method == 'BRBA':
              
            bu = band_red / band_swir2

        else:
            print("Invalid method specified.")
            return

        # Copy the metadata of the original image
        meta = src.meta

        # Update the metadata to reflect the number of layers and data type
        meta.update(count=1, dtype='float32')

        # Write the BU to a new file
        with rasterio.open(output_path, 'w', **meta) as dst:
            dst.write(bu, 1)

        # Print explanation of the method
        print("Method:", method)
        print("Formula:")
        print(explanation)

def check_alignment(image1_path, image2_path):
    with rasterio.open(image1_path) as src1, rasterio.open(image2_path) as src2:
        # Check CRS
        if src1.crs != src2.crs:
            print("CRS does not match.")
            return False
        
        # Check Affine Transform
        if src1.transform != src2.transform:
            print("Affine transform does not match.")
            return False
        
        # Check Bounding Box
        if src1.bounds != src2.bounds:
            print("Bounding box does not match.")
            return False

        print("Images are aligned.")
        return True

# Paths to the input GeoTIFF files
image1_path = 'S2A_MSIL1C_20240214T100121_N0510_R122_T33TTG_20240214T104957_resampled_rome.tif'
image2_path = 'S2A_MSIL1C_20230818T100031_N0509_R122_T33TTG_20230818T121434_resampled_rome.tif'

# Paths to the output GeoTIFF files
output1_path = 'S2A_MSIL1C_20240214T100121_N0510_R122_T33TTG_20240214T104957_resampled_rome_output1_bu1.tif'
output2_path = 'S2A_MSIL1C_20230818T100031_N0509_R122_T33TTG_20230818T121434_resampled_rome_output2_bu1.tif'

# Specify the method for BU calculation
method = 'EBUI'  # Change this to the desired method

# Calculate BU for each image and save the results
calculate_bu(image1_path, output1_path, method)
calculate_bu(image2_path, output2_path, method)

# Check alignment of the images
aligned = check_alignment(image1_path, image2_path)

if not aligned:
    print("Images are not aligned. Further processing may be required.")
else:
    print("BU calculation complete. Output images saved.")
