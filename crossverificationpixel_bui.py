#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 16:35:01 2024

@author: aneesha
"""

import rasterio
from pyproj import Transformer
import numpy as np

def get_pixel_value(image_path, lat, lon):
    with rasterio.open(image_path) as src:
        # Transform geographic coordinates to image coordinates
        transformer = Transformer.from_crs("EPSG:4326", src.crs, always_xy=True)
        x, y = transformer.transform(lon, lat)
        
        # Get pixel values at the transformed coordinates
        row, col = src.index(x, y)
        pixel_value = src.read(1)[row, col]
        
        return pixel_value

# Specify the geographic coordinates
#latitude = 41.91676207012941
#longitude = 12.423249863753226
latitude = 41.91638085797895
longitude =  12.423027274073522
# Paths to the input GeoTIFF files

image1_path = 'S2A_MSIL1C_20230818T100031_N0509_R122_T33TTG_20230818T121434_resampled_bu_rome_TRIAL.tif'
image2_path = 'S2A_MSIL1C_20240214T100121_N0510_R122_T33TTG_20240214T104957_resampled_bu_rome_TRIAL.tif'
# Get pixel values from both images
pixel_value_image1 = get_pixel_value(image1_path, latitude, longitude)
pixel_value_image2 = get_pixel_value(image2_path, latitude, longitude)

print(f"Pixel value at ({latitude}, {longitude}) in Image 1: {pixel_value_image1}")
print(f"Pixel value at ({latitude}, {longitude}) in Image 2: {pixel_value_image2}")

""" runfile('/home/aneesha/change_detection/untitled0.py', wdir='/home/aneesha/change_detection')
Pixel value at (41.91676207012941, 12.423249863753226) in Image 1: -0.468593955039978
Pixel value at (41.91676207012941, 12.423249863753226) in Image 2: -0.43824586272239685"""   #method -NDBI 

mean = (np.abs(pixel_value_image1)+np.abs(pixel_value_image2))/ 2 
diff = (np.abs(pixel_value_image2)-np.abs(pixel_value_image1))
print(f"Mean Pixel value at ({latitude}, {longitude}) in Image 1 & 2: {mean}")
print(f"diff Pixel value at ({latitude}, {longitude}) in Image 1 & 2: {diff}")