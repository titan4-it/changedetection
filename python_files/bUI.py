#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 15:03:02 2024

@author: aneesha
"""

import rasterio
import numpy as np
import matplotlib.pyplot as plt

def calculate_bu(image_path, output_path):
    with rasterio.open(image_path) as src:
        # Read Band 4 (Red), Band 5 (Vegetation Red Edge), Band 6 (Vegetation Red Edge), and Band 8 (NIR)
        band4 = src.read(4).astype('float32')
        band5 = src.read(5).astype('float32')
        band6 = src.read(6).astype('float32')

        # Avoid division by zero by adding a small constant (epsilon)
        epsilon = np.finfo(float).eps

        # Calculate NDVI
        ndvi = (band5 - band4) / (band5+ band4 + epsilon)

        # Calculate NDBI
        ndbi = (band6 - band5) / (band6 + band5 + epsilon)

        # Calculate Built-Up Index (BU)
        bu = ndvi - ndbi

        # Copy the metadata of the original image
        meta = src.meta

        # Update the metadata to reflect the number of layers and data type
        meta.update(count=1, dtype='float32')

        # Write the BU to a new file
        with rasterio.open(output_path, 'w', **meta) as dst:
            dst.write(bu, 1)

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
        diff = np.abs(bu2) - np.abs(bu1)
        
        # Apply threshold if specified
        if threshold is not None:
            change_map = np.abs(diff) < threshold
            diff = change_map.astype('float32')

        # Copy the metadata of the original image
        meta = src1.meta

        # Update the metadata to reflect the number of layers and data type
        meta.update(count=1, dtype='float32')

        # Write the difference to a new file
        with rasterio.open(output_diff_path, 'w', **meta) as dst:
            dst.write(diff, 1)
        return diff

def plot_histogram(data, title):
    # Flatten the data and remove nan values
    data = data.flatten()
    data = data[~np.isnan(data)]
    
    # Plot the histogram
    plt.figure(figsize=(10, 6))
    plt.hist(data, bins=50, color='blue', alpha=0.7)
    plt.title(title)
    plt.xlabel('Pixel Values')
    plt.ylabel('')
    plt.grid(True)
    plt.show()
    
image1_path = 'S2A_MSIL1C_20230818T100031_N0509_R122_T33TTG_20230818T121434_resampled_rome.tif'
image2_path = 'S2A_MSIL1C_20240214T100121_N0510_R122_T33TTG_20240214T104957_resampled_rome.tif'

# Paths to the output GeoTIFF files
output1_path = 'S2A_MSIL1C_20230818T100031_N0509_R122_T33TTG_20230818T121434_resampled_bu_rome_TRIAL.tif'
output2_path = 'S2A_MSIL1C_20240214T100121_N0510_R122_T33TTG_20240214T104957_resampled_bu_rome_TRIAL.tif'
output_diff_path ='bui_difference.tif'
threshold = 0.0001

# Calculate BU for each image and save the results
calculate_bu(image1_path, output1_path)
calculate_bu(image2_path, output2_path)

# Check alignment of the images
aligned = check_alignment(image1_path, image2_path)

if not aligned:
    print("Images are not aligned. Further processing may be required.")
else:
    # Compute the difference between the two BU images and save the result
    diff_data=compute_difference(output1_path, output2_path, output_diff_path, threshold)
    print("Difference calculation complete. Output image saved.")
    plot_histogram(diff_data, 'Histogram of difference Pixel Values')
   
    
