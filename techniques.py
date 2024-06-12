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
            bu = (band_swir - band_nir) / (band_swir + band_nir + epsilon)
            explanation = "Normalized Difference Built-up Index (NDBI):\nNDBI = (SWIR - NIR) / (SWIR + NIR)"
        elif method == 'MBUI':
            # Modified Built-up Index (MBUI)
            bu = (2 * (band_swir - band_nir) - (band_green - band_red)) / (2 * (band_swir - band_nir) + (band_green - band_red) + epsilon)
            explanation = "Modified Built-up Index (MBUI):\nMBUI = (2 * (SWIR - NIR) - (Green - Red)) / (2 * (SWIR - NIR) + (Green - Red))"
        elif method == 'BUAI':
            # Built-Up Area Index (BUAI)
            bu = (band_green + band_swir) / (band_red + band_nir + epsilon)
            explanation = "Built-Up Area Index (BUAI):\nBUAI = (Green + SWIR) / (Red + NIR)"
        elif method == 'SR':
            # Simple Ratio (SR)
            bu = band_swir / (band_nir + epsilon)
            explanation = "Simple Ratio (SR):\nSR = SWIR / NIR"
        elif method == 'EBUI':
            # Enhanced Built-Up Index (EBUI)
            bu = (2 * (band_swir - band_nir) - (band_red - band_green)) / (2 * (band_swir - band_nir) + (band_red - band_green) + epsilon)
            explanation = "Enhanced Built-Up Index (EBUI):\nEBUI = (2 * (SWIR - NIR) - (Red - Green)) / (2 * (SWIR - NIR) + (Red - Green))"
        elif method == 'UI':
            # Urban Index (UI)
            bu = (band_blue + 2.5 * band_green - 1.5 * band_swir - band_nir) / (band_blue + 2.5 * band_green - 1.5 * band_swir + band_nir + epsilon)
            explanation = "Urban Index (UI):\nUI = (Blue + 2.5 * Green - 1.5 * SWIR - NIR) / (Blue + 2.5 * Green - 1.5 * SWIR + NIR)"
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
image1_path = 'S2B_MSIL1C_20230728T093549_N0509_R036_T33TXF_20230728T102944_resampled.tif'
image2_path = 'S2B_MSIL1C_20230827T093549_N0509_R036_T33TXF_20230827T114636_resampled.tif'

# Paths to the output GeoTIFF files
output1_path = 'S2B_MSIL1C_20230728T093549_N0509_R036_T33TXF_20230728T102944_resampled_output1_bu1.tif'
output2_path = 'S2B_MSIL1C_20230827T093549_N0509_R036_T33TXF_20230827T114636_resampled_output2_bu1.tif'

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
