#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 11:30:21 2024

@author: aneesha
"""

import rasterio
import numpy as np
import matplotlib.pyplot as plt

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
    
def calculate_bu(image_path, output_path, method):
    with rasterio.open(image_path) as src:
        band_red = src.read(4).astype('float32') / 10000
        plot_histogram(band_red, 'Histogram of band_red')
        band_green = src.read(3).astype('float32') / 10000
        plot_histogram(band_green, 'Histogram of band_green')
        band_blue = src.read(2).astype('float32') / 10000
        plot_histogram(band_blue, 'Histogram of band_blue')
        band_nir = src.read(8).astype('float32') / 10000
        plot_histogram(band_nir, 'Histogram of band_nir')
        band_swir = src.read(11).astype('float32') / 10000
        plot_histogram(band_swir, 'Histogram of band_swir')

        epsilon = np.finfo(float).eps

        if method == 'NDBI':
            bu = (band_swir - band_nir) / (band_swir + band_nir + epsilon)
        else:
            print("Invalid method specified.")
            return

        meta = src.meta
        meta.update(count=1, dtype='float32')

        with rasterio.open(output_path, 'w', **meta) as dst:
            dst.write(bu, 1)

def compute_difference(image1_path, image2_path, output_diff_path, threshold=None):
    with rasterio.open(image1_path) as src1, rasterio.open(image2_path) as src2:
        bu1 = src1.read(1).astype('float32')
        bu2 = src2.read(1).astype('float32')
        diff = bu2 - bu1
        
        if threshold is not None:
            change_map = np.abs(diff) > threshold
            diff = change_map.astype('float32')

        meta = src1.meta
        meta.update(count=1, dtype='float32')

        with rasterio.open(output_diff_path, 'w', **meta) as dst:
            dst.write(diff, 1)

def compute_mean(image1_path, image2_path, output_mean_path):
    with rasterio.open(image1_path) as src1, rasterio.open(image2_path) as src2:
        bu1 = src1.read(1).astype('float32')
        bu2 = src2.read(1).astype('float32')
        mean = (bu1 + bu2) / 2
        
        meta = src1.meta
        meta.update(count=1, dtype='float32')

        with rasterio.open(output_mean_path, 'w', **meta) as dst:
            dst.write(mean, 1)

def match_urban_pixels(landcover_path, diff_path, mean_path, urban_value=1):
    with rasterio.open(landcover_path) as lc_src:
        lc_data = lc_src.read(1).astype('float32')

    with rasterio.open(diff_path) as diff_src:
        diff_data = diff_src.read(1).astype('float32')

    with rasterio.open(mean_path) as mean_src:
        mean_data = mean_src.read(1).astype('float32')

    urban_mask = lc_data == urban_value
    urban_diff_values = diff_data[urban_mask]
    urban_mean_values = mean_data[urban_mask]

    plt.figure(figsize=(20, 10))
    
    # Plot land cover classification with urban areas
    plt.subplot(2, 3, 1)
    plt.imshow(lc_data, cmap='viridis')
    plt.colorbar(label='Land Cover Classification')
    plt.imshow(urban_mask, cmap='Reds', alpha=0.5)
    plt.title('Land Cover with Urban Areas Highlighted')
    
    # Plot difference image
    plt.subplot(2, 3, 2)
    plt.imshow(diff_data, cmap='coolwarm')
    plt.colorbar(label='Difference Value')
    plt.title('Difference Image')
    
    # Plot mean image
    plt.subplot(2, 3, 3)
    plt.imshow(mean_data, cmap='YlGn')
    plt.colorbar(label='Mean Value')
    plt.title('Mean Image')

    # Plot histogram of difference values for urban areas
    plt.subplot(2, 3, 4)
    plt.hist(urban_diff_values, bins=30, color='blue', alpha=0.7)
    plt.xlabel('Difference Value')
    plt.ylabel('Frequency')
    plt.title('Histogram of Difference Values for Urban Areas')

    # Plot histogram of mean values for urban areas
    plt.subplot(2, 3, 5)
    plt.hist(urban_mean_values, bins=30, color='green', alpha=0.7)
    plt.xlabel('Mean Value')
    plt.ylabel('Frequency')
    plt.title('Histogram of Mean Values for Urban Areas')
    
    plt.tight_layout()
    plt.show()

# Paths to the input and output files
landcover_image_path = 'landcover_matera1.tif'
image1_path = 'S2B_MSIL1C_20230728T093549_N0509_R036_T33TXF_20230728T102944_matera.tif'
image2_path = 'S2B_MSIL1C_20230827T093549_N0509_R036_T33TXF_20230827T114636_matera.tif'
output_bu1_path = 'bu_output1.tif'
output_bu2_path = 'bu_output2.tif'
output_diff_path = 'difference_bu.tif'
output_mean_path = 'mean_bu.tif'

# Calculate BU for each image
method = 'NDBI'
calculate_bu(image1_path, output_bu1_path, method)
calculate_bu(image2_path, output_bu2_path, method)

# Compute the difference and mean images
threshold = 0.2
compute_difference(output_bu1_path, output_bu2_path, output_diff_path, threshold)
compute_mean(output_bu1_path, output_bu2_path, output_mean_path)

# Match and analyze urban pixels
match_urban_pixels(landcover_image_path, output_diff_path, output_mean_path, urban_value=1)
