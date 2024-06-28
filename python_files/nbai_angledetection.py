#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 11:43:30 2024

@author: aneesha
"""

import rasterio
import numpy as np
import matplotlib.pyplot as plt

def calculate_bu(image_path, output_path, method):
    with rasterio.open(image_path) as src:
        # Read the required spectral bands
        band_red = src.read(4).astype('float32') / 10000
        band_green = src.read(3).astype('float32')/ 10000
        band_blue = src.read(2).astype('float32')/ 10000
        band_nir = src.read(8).astype('float32') / 10000
        band_swir = src.read(11).astype('float32') / 10000
        band_swir2 = src.read(12).astype('float32') / 10000
        # Avoid division by zero by adding a small constant (epsilon)
        #plot_histogram(band_red, 'Histogram of band_red')
        #plot_histogram(band_green, 'Histogram of band_green')
        #plot_histogram(band_blue, 'Histogram of band_blue')
        #plot_histogram(band_nir, 'Histogram of band_nir')
        #plot_histogram(band_swir, 'Histogram of band_swir')
        #plot_histogram(band_swir2, 'Histogram of band_swir2')
     
       # Calculate the Built-Up Index (BU) based on the specified method
        if method == 'NDBI':
           # Normalized Difference Built-up Index (NDBI)
           bu = (band_swir2 - band_nir) / (band_swir2 + band_nir )
        elif method == 'NDVI':
           bu = (band_nir - band_red) / (band_nir + band_red)

        elif method == 'NBAI':
           # 
           bu = (band_swir2 - band_swir)/ band_green 

        elif method == 'NBI':
           # 
           bu = (band_red * band_swir2) / (band_nir )

        elif method == 'MBI':
           # 
           bu = ((band_swir * band_red) - (band_nir * band_nir)) / (band_red + band_nir + band_swir)

        elif method == 'UI':
           # Urban Index (UI)
           bu = (band_swir - band_nir)/(band_swir + band_nir)
           
        elif method == 'BAEI':
               
           bu = (band_red + 0.3) / (band_green + band_swir)

        elif method == 'BRBA':
             
           bu = band_red / band_swir2
        elif method == 'new_BUI':
                
              bu = ((band_red + band_green) - (band_blue + band_nir)) / ((band_red + band_green) + (band_blue + band_nir))
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
        return bu
        # Print explanation of the method
        print("Method:", method)

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
        diff = bu1 - bu2
        
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
        return diff
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
        return mean
def plot_histogram(data, title):
    # Flatten the data and remove nan values
    data = data.flatten()
    data = data[~np.isnan(data)]
    
    # Plot the histogram
    plt.figure(figsize=(10, 6))
    plt.hist(data, bins=50, color='blue', alpha=0.7)
    plt.title(title)
    plt.xlabel('Mean Value - Builtup Index')
    plt.ylabel('pixels')
    plt.grid(True)
    plt.show()
# Paths to the input GeoTIFF files
image1_path = 'S2A_MSIL1C_20230818T100031_N0509_R122_T33TTG_20230818T121434_rome_bilinear.tif'
image2_path = 'S2A_MSIL1C_20240214T100121_N0510_R122_T33TTG_20240214T104957_rome_bilinear.tif'

# Paths to the output GeoTIFF files
output1_path = 'S2A_MSIL1C_20230818T100031_N0509_R122_T33TTG_20230818T121434_rome_bilinear_TRIAL.tif'
output2_path = 'S2A_MSIL1C_20240214T100121_N0510_R122_T33TTG_20240214T104957_rome_bilinear_TRIAL.tif'
output_diff_path = 'difference_bu_rome_bilinear_TRIAL.tif'
output_mean_path = 'mean_bu_rome_bilinear_TRIAL.tif'

# Specify the method for BU calculation
method = 'NBAI'  # Change this to the desired method

# Specify the threshold for change detection (set to None if not using a threshold)
threshold = 0.9 # Adjust this value based on your analysis

# Calculate BU for each image and save the results
bu1 = calculate_bu(image1_path, output1_path, method)
#plot_histogram(bu1, 'Histogram of bu1 Pixel Values')
bu2 = calculate_bu(image2_path, output2_path, method)
#plot_histogram(bu2, 'Histogram of bu2 Pixel Values')
# Check alignment of the images
aligned = check_alignment(image1_path, image2_path)

if not aligned:
    print("Images are not aligned. Further processing may be required.")
else:
    # Compute the difference between the two BU images and save the result
    diff_data=compute_difference(output1_path, output2_path, output_diff_path, threshold)
    print("Difference calculation complete. Output image saved.")
   # plot_histogram(diff_data, 'Histogram of difference Pixel Values')
    # Compute the mean of the two BU images and save the result
    mean_data = compute_mean(output1_path, output2_path, output_mean_path)
    print("Mean calculation complete. Output image saved.")
    plot_histogram(mean_data, 'Histogram of Mean Pixel Values')