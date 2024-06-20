#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 11:39:36 2024

@author: aneesha
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 11:43:30 2024

@author: aneesha
"""

import rasterio
import numpy as np

def calculate_bu(image_path, output_path, method):
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
            # Normalized Difference Built-up Index (NDBI)
            bu = (band_swir - band_nir) / (band_swir + band_nir + epsilon)
            explanation = "Normalized Difference Built-up Index (NDBI):\nNDBI = (SWIR - NIR) / (SWIR + NIR)"
        elif method == 'NBI':
            # New Built-up Index (NBI)
            bu = (band_red * band_swir) / (band_nir + epsilon)
            explanation = "New Build-up Index:\nNBI = (Red * SWIR)/( NIR) "
        elif method == 'NBAI':
            # Normalized Built-Up Area Index (NBAI)
            bu = ((band_swir2 - band_swir) / (band_green + epsilon))/((band_swir2 + band_swir) / (band_green + epsilon ))
            explanation = "Normalized Built-Up Area Index (NBAI):\nNBAI =((SWIR2 - SWIR) / (Green)) /( (SWIR2 + SWIR) / (Green))" 
        elif method == 'MBI':
            # Modified Built-Up Index (MBI)
            bu = ( (band_swir * band_red) - (band_nir * band_nir)) / (band_red + band_nir + band_swir + epsilon)
            explanation = "Modified Built-Up Index (MBI) :\nNBAI = (SWIR * RED) - (NIR * NIR)) / (RED + NIR + SWIR)"
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

def compute_difference(image1_path, image2_path, output_diff_path, threshold=None):
    with rasterio.open(image1_path) as src1, rasterio.open(image2_path) as src2:
        bu1 = src1.read(1).astype('float32')
        bu2 = src2.read(1).astype('float32')
        
        # Compute the difference
        diff = bu2 - bu1
        
        # Apply threshold if specified
        if threshold is not None:
            change_map = np.abs(diff) > threshold
            diff = change_map.astype('float32')

        # Copy the metadata of the original image
        meta = src1.meta

        # Update the metadata to reflect the number of layers and data type
        meta.update(count=1, dtype='float32')

        # Write the difference to a new file
        with rasterio.open(output_diff_path, 'w', **meta) as dst:
            dst.write(diff, 1)

def compute_mean(image1_path, image2_path, output_mean_path):
    with rasterio.open(image1_path) as src1, rasterio.open(image2_path) as src2:
        bu1 = src1.read(1).astype('float32')
        bu2 = src2.read(1).astype('float32')
        
        # Compute the mean
        mean = (bu1 + bu2) / 2
        
        # Copy the metadata of the original image
        meta = src1.meta

        # Update the metadata to reflect the number of layers and data type
        meta.update(count=1, dtype='float32')

        # Write the mean to a new file
        with rasterio.open(output_mean_path, 'w', **meta) as dst:
            dst.write(mean, 1)

# Paths to the input GeoTIFF files
image1_path = 'S2A_MSIL1C_20230818T100031_N0509_R122_T33TTG_20230818T121434_resampled_rome.tif'
image2_path = 'S2A_MSIL1C_20240214T100121_N0510_R122_T33TTG_20240214T104957_resampled_rome.tif'

# Paths to the output GeoTIFF files
output1_path = 'S2A_MSIL1C_20230818T100031_N0509_R122_T33TTG_20230818T121434_resampled_bu_rome.tif'
output2_path = 'S2A_MSIL1C_20240214T100121_N0510_R122_T33TTG_20240214T104957_resampled_bu_rome.tif'
output_diff_path = 'difference_bu_rome_ndbi.tif'
output_mean_path = 'mean_bu_rome_ndbi.tif'

# Specify the method for BU calculation
method = 'NDBI'  # Change this to the desired method

# Specify the threshold for change detection (set to None if not using a threshold)
threshold = 0.25  # Adjust this value based on your analysis

# Calculate BU for each image and save the results
calculate_bu(image1_path, output1_path, method)
calculate_bu(image2_path, output2_path, method)

# Check alignment of the images
aligned = check_alignment(image1_path, image2_path)

if not aligned:
    print("Images are not aligned. Further processing may be required.")
else:
    # Compute the difference between the two BU images and save the result
    compute_difference(output1_path, output2_path, output_diff_path, threshold)
    print("Difference calculation complete. Output image saved.")
    
    # Compute the mean of the two BU images and save the result
    compute_mean(output1_path, output2_path, output_mean_path)
    print("Mean calculation complete. Output image saved.")
