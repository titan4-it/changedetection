#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 15:03:02 2024

@author: aneesha
"""

import rasterio
import numpy as np

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

# Paths to the input GeoTIFF files
image1_path = 'S2B_MSIL1C_20230728T093549_N0509_R036_T33TXF_20230728T102944_matera.tif'
image2_path = 'S2B_MSIL1C_20230827T093549_N0509_R036_T33TXF_20230827T114636_matera.tif'

# Paths to the output GeoTIFF files
output1_path = 'S2B_MSIL1C_20230728T093549_N0509_R036_T33TXF_20230728T102944_bu.tif'
output2_path = 'S2B_MSIL1C_20230827T093549_N0509_R036_T33TXF_20230827T114636_bu.tif'

# Calculate BU for each image and save the results
calculate_bu(image1_path, output1_path)
calculate_bu(image2_path, output2_path)

# Check alignment of the images
aligned = check_alignment(image1_path, image2_path)

if not aligned:
    print("Images are not aligned. Further processing may be required.")
