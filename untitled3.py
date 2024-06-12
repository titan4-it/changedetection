#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 16:55:47 2024

@author: aneesha
"""

import rasterio
import numpy as np
import matplotlib.pyplot as plt

# Function to calculate Normalized Difference Built-up Index (NDBI)
def calculate_ndbi(nir, swir):
    bu = (swir - nir) / (swir + nir)
    return bu

# Function to calculate Index-based Built-up Index (IBI)
def calculate_ibi(nir, swir, red, green):
    ndbi = calculate_ndbi(nir, swir)
    savi = ((nir - red) * 1.5) / (nir + red + 0.5)
    ndwi = (green - nir) / (green + nir)
    bu = (ndbi - (savi + ndwi) / 2) / (ndbi + (savi + ndwi) / 2)
    return bu

def calculate_bu(image_path, output_path, method):
    with rasterio.open(image_path) as src:
        # Read the required spectral bands
        red = src.read(4).astype('float32')
        green = src.read(3).astype('float32')
        nir = src.read(8).astype('float32')
        swir = src.read(11).astype('float32')

        if method == 'ndbi':
            bu = calculate_ndbi(nir, swir)
        elif method == 'ibi':
            bu = calculate_ibi(nir, swir, red, green)
        else: 
            print('No valid method selected')
            return

        # Copy the metadata of the original image
        meta = src.meta

        # Update the metadata to reflect the number of layers and data type
        meta.update(count=1, dtype='float32')

        # Write the BU to a new file
        with rasterio.open(output_path, 'w', **meta) as dst:
            dst.write(bu, 1)

# Paths to the input GeoTIFF files
image_path = 'S2B_MSIL1C_20230728T093549_N0509_R036_T33TXF_20230728T102944_resampled.tif'

# Paths to the output GeoTIFF files
output_path = 'S2B_MSIL1C_20230728T093549_N0509_R036_T33TXF_20230728T102944_resampled_output_bu.tif'

# Method to use for calculation (ndbi or ibi)
method = 'ndbi'

# Calculate the built-up index and save the result
calculate_bu(image_path, output_path, method)
