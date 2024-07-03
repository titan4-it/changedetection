#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 10:36:37 2024

@author: aneesha
"""

import rasterio
import numpy as np
import matplotlib.pyplot as plt
from rasterio.warp import calculate_default_transform, reproject, Resampling, transform

def read_image(image_path):
    with rasterio.open(image_path) as src:
        image_data = src.read().astype('float32') / 10000
        meta = src.meta
    return image_data, meta

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

def apply_mask(image_data, mask_data):
    masked_image = np.where(mask_data == 1, image_data, np.nan)
    return masked_image
#trying to mask the images
def calculate_bu(masked_image):
    band_4 = masked_image[4]
    band_8 = masked_image[8]
    band_11 = masked_image[12]
   
    epsilon = np.finfo(float).eps
    ndvi = (band_8 - band_4) / (band_8 + band_4 + epsilon)
    ndbi = (band_11 - band_8) / (band_11 + band_8 + epsilon)
    bu = ndvi - ndbi
    return bu

def reproject_coordinates(coords, src_crs, dst_crs):
    projected_coords = []
    for lon, lat in coords:
        x, y = transform(src_crs, dst_crs, [lon], [lat])
        projected_coords.append((x[0], y[0]))
    return projected_coords

def extract_pixel_values(image_path, coordinates):
    with rasterio.open(image_path) as src:
        pixel_values = []
        for coord in coordinates:
            row, col = src.index(coord[0], coord[1])  # Note: (longitude, latitude)
            if 0 <= row < src.height and 0 <= col < src.width:
                pixel_values.append(src.read(1)[row, col])
            else:
                pixel_values.append(np.nan)
    return pixel_values

def plot_pixel_values(pixel_values):
    plt.figure(figsize=(10, 5))
    plt.plot(pixel_values, marker='o')
    plt.xlabel('Coordinate Index')
    plt.ylabel('BU Difference Value')
    plt.title('BU Difference Values at Specified Coordinates')
    plt.grid(True)
    plt.show()
def plot_pixel_values_bu(pixel_values_bu1,pixel_values_bu2):
    plt.figure(figsize=(10, 5))   
    plt.plot(pixel_values_bu1, marker='o')   
    plt.plot(pixel_values_bu2, marker='.')
    plt.xlabel('Coordinate Index')
    plt.ylabel('BU  Value')
    plt.title('BU  Values at Specified Coordinates')
    plt.legend(['BU1', 'BU2'])
    plt.grid(True)
    plt.show()
# Paths to the input and output files
landcover_image_path = '/Users/aneesha_work/Documents/Images_Sentinel2/Rome_landcover.tif'
image1_path = '/Users/aneesha_work/Documents/Images_Sentinel2/Images_Sentinel2/S2A_MSIL1C_20240214T100121_N0510_R122_T33TTG_20240214T104957_resampled_rome.tif'
image2_path = '/Users/aneesha_work/Documents/Images_Sentinel2/Images_Sentinel2/S2A_MSIL1C_20230818T100031_N0509_R122_T33TTG_20230818T121434_resampled_rome.tif'
output_bu1_path = '/Users/aneesha_work/Documents/Images_Sentinel2/bu_output1.tif'
output_bu2_path = '/Users/aneesha_work/Documents/Images_Sentinel2/bu_output2.tif'
output_diff_path = '/Users/aneesha_work/Documents/Images_Sentinel2/difference_bu.tif'
reprojected_landcover_path = '/Users/aneesha_work/Documents/Images_Sentinel2/reprojected_landcover.tif'
# Coordinates for pixel value extraction (longitude, latitude)
coordinates = [
    (12.423027274073522, 41.91638085797895),
    (12.42212071335914, 41.91657450073516),
    (12.422270917060224, 41.9156903193817),
    (12.42282881653152, 41.91588392221169),
    (12.422295056939985, 41.915129466623036),
    (12.424164556610625, 41.914959812684955),
    (12.424864613158745, 41.915171381055956),
    (12.401223623062545, 41.91573822115919),
    (12.401352369094383, 41.90583775468933),
    (12.430534802977597, 41.91765426311034),
]
# Read images and mask
image1_data, meta = read_image(image1_path)
image2_data, _ = read_image(image2_path)
# Create urban mask
mask_path = create_urban_mask(landcover_image_path, urban_value=7)
with rasterio.open(mask_path) as mask_src:
    urban_mask = mask_src.read(1)
# Apply mask to images
masked_image1 = apply_mask(image1_data, urban_mask)
masked_image2 = apply_mask(image2_data, urban_mask)
# Calculate BU for each masked image
bu1 = calculate_bu(masked_image1)
bu2 = calculate_bu(masked_image2)
# Save BU images
meta.update(count=1, dtype='float32')
with rasterio.open(output_bu1_path, 'w', **meta) as dst:
    dst.write(bu1, 1)
with rasterio.open(output_bu2_path, 'w', **meta) as dst:
    dst.write(bu2, 1)
# Compute the difference image

# Define the threshold range
threshold_min = -0.3
threshold_max = 0.3
no_data_value = np.nan  # Define your no data value


# Apply threshold to bu1
bu1 = np.where((bu1 >= threshold_min) & (bu1 <= threshold_max), bu1, no_data_value)

# Apply threshold to bu2
bu2 = np.where((bu2 >= threshold_min) & (bu2 <= threshold_max), bu2, no_data_value)

# Save the thresholded bu1
with rasterio.open(output_bu1_path, 'w', **meta) as dst:
    dst.write(bu1, 1)

# Save the thresholded bu2
with rasterio.open(output_bu2_path, 'w', **meta) as dst:
    dst.write(bu2, 1)

# Compute the difference image
diff = bu1 - bu2

# Save the difference image
with rasterio.open(output_diff_path, 'w', **meta) as dst:
    dst.write(diff, 1)
# Reproject the coordinates to the image CRS
with rasterio.open(output_diff_path) as src:
    image_crs = src.crs
reprojected_coords = reproject_coordinates(coordinates, 'EPSG:4326', image_crs)  # Assuming coordinates are in 'EPSG:4326'
# Extract pixel values from the difference image
pixel_values_diff = extract_pixel_values(output_diff_path, reprojected_coords)
pixel_values_bu1 = extract_pixel_values(output_bu1_path, reprojected_coords)
pixel_values_bu2 = extract_pixel_values(output_bu2_path, reprojected_coords)
# Plot the pixel values
plot_pixel_values(pixel_values_diff)
plot_pixel_values_bu(pixel_values_bu1,pixel_values_bu2)
def plot_results(landcover_path, bu1_path, bu2_path, diff_path, coordinates):
    with rasterio.open(landcover_path) as lc_src:
        lc_data = lc_src.read(1).astype('float32')
    with rasterio.open(bu1_path) as bu1_src:
        bu1_data = bu1_src.read(1).astype('float32')
    with rasterio.open(bu2_path) as bu2_src:
        bu2_data = bu2_src.read(1).astype('float32')
    with rasterio.open(diff_path) as diff_src:
        diff_data = diff_src.read(1).astype('float32')
    urban_mask = (lc_data == 7)
    plt.figure(figsize=(20, 10))    
    # Plot land cover with urban areas highlighted
    plt.subplot(2, 2, 1)
    plt.imshow(lc_data, cmap='viridis')
    plt.colorbar(label='Land Cover Classification')
    plt.imshow(urban_mask, cmap='Reds', alpha=0.5)
    plt.title('Land Cover with Urban Areas Highlighted')  
    # Plot bu1
    plt.subplot(2, 2, 3)
    plt.imshow(bu1_data, cmap='coolwarm')
    plt.colorbar(label='BU1 Value',boundaries=[-0.6,-0.4,-0.2,0,0.2,0.4,0.6],ticklocation='auto')
    plt.title('BU1 Image')  
    # Plot bu2
    plt.subplot(2, 2, 4)
    plt.imshow(bu2_data, cmap='coolwarm')
    plt.colorbar(label='BU2 Value',boundaries=[-0.6,-0.4,-0.2,0,0.2,0.4,0.6],ticklocation='auto')
    plt.title('BU2 Image')
    # Plot difference image
    plt.subplot(2, 2, 2)
    plt.imshow(diff_data, cmap='coolwarm')
    plt.colorbar(label='Difference Value')
    plt.title('Difference Image')
    # Show the plots
    plt.tight_layout()
    plt.show()

# Call the function to plot results
plot_results(landcover_image_path, output_bu1_path, output_bu2_path, output_diff_path, coordinates)
