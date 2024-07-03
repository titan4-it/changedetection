#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 10:36:37 2024

@author: aneesha
"""

import rasterio
import numpy as np
import matplotlib.pyplot as plt
from rasterio.warp import calculate_default_transform, reproject, Resampling

def calculate_bu(image_path, output_path):
    with rasterio.open(image_path) as src:
        band_red = src.read(4).astype('float32') / 10000
        band_green = src.read(3).astype('float32') / 10000
        band_blue = src.read(2).astype('float32') / 10000
        band_nir = src.read(8).astype('float32') / 10000
        band_swir = src.read(12).astype('float32') / 10000
        band_5 = src.read(5).astype('float32') / 10000
        band_6 = src.read(6).astype('float32') / 10000

        epsilon = np.finfo(float).eps
        
        ndvi = (band_5 - band_red) / (band_5 + band_red + epsilon)
        ndbi = (band_6 - band_5) / (band_6 + band_5 + epsilon)
        bu = ndvi - ndbi

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

def reproject_to_match(src_path, match_path, output_path):
    with rasterio.open(src_path) as src:
        with rasterio.open(match_path) as match:
            transform, width, height = calculate_default_transform(
                src.crs, match.crs, match.width, match.height, *match.bounds)
            kwargs = src.meta.copy()
            kwargs.update({
                'crs': match.crs,
                'transform': transform,
                'width': width,
                'height': height
            })

            with rasterio.open(output_path, 'w', **kwargs) as dst:
                for i in range(1, src.count + 1):
                    reproject(
                        source=rasterio.band(src, i),
                        destination=rasterio.band(dst, i),
                        src_transform=src.transform,
                        src_crs=src.crs,
                        dst_transform=transform,
                        dst_crs=match.crs,
                        resampling=Resampling.nearest)

def create_urban_mask(landcover_path, urban_value=7):
    with rasterio.open(landcover_path) as lc_src:
        lc_data = lc_src.read(1).astype('float32')
        urban_mask = (lc_data == urban_value).astype('float32')
        
        meta = lc_src.meta
        meta.update(count=1, dtype='float32')
        
        mask_output_path = 'urban_mask.tif'
        with rasterio.open(mask_output_path, 'w', **meta) as dst:
            dst.write(urban_mask, 1)
            
    return mask_output_path

def apply_mask(diff_path, mask_path, output_masked_diff_path):
    with rasterio.open(diff_path) as diff_src, rasterio.open(mask_path) as mask_src:
        diff_data = diff_src.read(1).astype('float32')
        mask_data = mask_src.read(1).astype('float32')
        
        masked_diff = np.where(mask_data == 1, diff_data, np.nan).astype('float32')
        
        meta = diff_src.meta
        meta.update(count=1, dtype='float32')
        
        with rasterio.open(output_masked_diff_path, 'w', **meta) as dst:
            dst.write(masked_diff, 1)

def plot_results(landcover_path, diff_path, masked_diff_path):
    with rasterio.open(landcover_path) as lc_src:
        lc_data = lc_src.read(1).astype('float32')
    with rasterio.open(diff_path) as diff_src:
        diff_data = diff_src.read(1).astype('float32')
    with rasterio.open(masked_diff_path) as masked_diff_src:
        masked_diff_data = masked_diff_src.read(1).astype('float32')

    urban_mask = (lc_data == 7)

    plt.figure(figsize=(20, 10))
    
    plt.subplot(2, 3, 1)
    plt.imshow(lc_data, cmap='viridis')
    plt.colorbar(label='Land Cover Classification')
    plt.imshow(urban_mask, cmap='Reds', alpha=0.5)
    plt.title('Land Cover with Urban Areas Highlighted')
    
    plt.subplot(2, 3, 2)
    plt.imshow(diff_data, cmap='coolwarm')
    plt.colorbar(label='Difference Value')
    plt.title('Difference Image')
    
    plt.subplot(2, 3, 3)
    plt.imshow(masked_diff_data, cmap='coolwarm')
    plt.colorbar(label='Difference Value')
    plt.title('Masked Difference Image')

    plt.subplot(2, 3, 4)
    urban_diff_values = masked_diff_data[~np.isnan(masked_diff_data)]
    plt.hist(urban_diff_values, bins=30, color='blue', alpha=0.7)
    plt.xlabel('Difference Value')
    plt.ylabel('Pixels')
    plt.title('Histogram of Difference Values for Urban Areas')

    plt.tight_layout()
    plt.show()

# Paths to the input and output files
#landcover_image_path = 'landcover_sentinelhub_rome.tif'
#image1_path = 'S2A_MSIL1C_20240214T100121_N0510_R122_T33TTG_20240214T104957_bilinear_rome.tif'
#image2_path = 'S2A_MSIL1C_20230818T100031_N0509_R122_T33TTG_20230818T121434_bilinear_rome.tif'
#output_bu1_path = 'bu_output1.tif'
#output_bu2_path = 'bu_output2.tif'
#output_diff_path = 'difference_bu.tif'
#output_masked_diff_path = 'masked_difference_bu.tif'
#reprojected_landcover_path = 'reprojected_landcover.tif'


landcover_image_path = '/Users/aneesha_work/Documents/Images_Sentinel2/Rome_landcover.tif'
image1_path = '/Users/aneesha_work/Documents/Images_Sentinel2/Images_Sentinel2/S2A_MSIL1C_20240214T100121_N0510_R122_T33TTG_20240214T104957_resampled_rome.tif'
image2_path = '/Users/aneesha_work/Documents/Images_Sentinel2/Images_Sentinel2/S2A_MSIL1C_20230818T100031_N0509_R122_T33TTG_20230818T121434_resampled_rome.tif'
output_bu1_path = '/Users/aneesha_work/Documents/Images_Sentinel2/bu_output1.tif'
output_bu2_path = '/Users/aneesha_work/Documents/Images_Sentinel2/bu_output2.tif'
output_diff_path = '/Users/aneesha_work/Documents/Images_Sentinel2/difference_bu.tif'
output_masked_diff_path = '/Users/aneesha_work/Documents/Images_Sentinel2/masked_difference_bu.tif'
reprojected_landcover_path = '/Users/aneesha_work/Documents/Images_Sentinel2/reprojected_landcover.tif'
# Calculate BU for each image
calculate_bu(image1_path, output_bu1_path)
calculate_bu(image2_path, output_bu2_path)

# Compute the difference image
threshold = None
compute_difference(output_bu1_path, output_bu2_path, output_diff_path, threshold)

# Reproject the landcover image to match the difference image
reproject_to_match(landcover_image_path, output_diff_path, reprojected_landcover_path)

# Create urban mask
mask_path = create_urban_mask(reprojected_landcover_path, urban_value=7)

# Apply urban mask to the difference image
apply_mask(output_diff_path, mask_path, output_masked_diff_path)

# Plot the results
plot_results(reprojected_landcover_path, output_diff_path, output_masked_diff_path)
