#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 11:26:31 2024

@author: aneesha
"""

import rasterio
import numpy as np
import matplotlib.pyplot as plt

def create_urban_plot(image_path, urban_value=1):
    # Read the landcover image
    with rasterio.open(image_path) as src:
        lc_data = src.read(1).astype('float32')
    
    # Mask urban areas
    urban_mask = lc_data == urban_value
    urban_values = lc_data[urban_mask]
    
    # Plot the land cover image and highlight urban areas
    plt.figure(figsize=(10, 10))
    plt.imshow(lc_data, cmap='viridis')
    plt.colorbar(label='Land Cover Classification')
    plt.imshow(urban_mask, cmap='Reds', alpha=0.5)
    plt.title('Land Cover with Urban Areas Highlighted')
    plt.show()

    # Plot histogram of land cover values for urban areas
    plt.figure(figsize=(8, 6))
    plt.hist(urban_values, bins=30, color='red', alpha=0.7)
    plt.xlabel('Land Cover Value')
    plt.ylabel('Frequency')
    plt.title('Histogram of Land Cover Values for Urban Areas')
    plt.show()

# Path to the input file
landcover_image_path = '/home/aneesha/change_detection/u2018_clc2018_v2020_20u1_raster100m/DATA/U2018_CLC2018_V2020_20u1.tif'

# Create the urban plot
create_urban_plot(landcover_image_path, urban_value=1)
