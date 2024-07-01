#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 14:56:27 2024

@author: aneesha
"""

import rasterio
from rasterio.enums import Resampling
import os

def unstack_bands(input_file, output_dir):
    # Open the input GeoTIFF file
    with rasterio.open(input_file) as src:
        # Get the number of bands
        num_bands = src.count

        # Ensure the input file has 12 bands
        if num_bands != 13:
            raise ValueError(f"Expected 13 bands, but found {num_bands} bands in the input file.")

        # Extract the base name of the input file for constructing output file names
        base_name = os.path.splitext(os.path.basename(input_file))[0]

        # Define the prefix and suffix for the output file names
        #prefix = "S2A_MSIL1C_20230818T100031_N0509_R122_T33TTG_20230818T121434_B0"

        # Loop through each band and save it as a separate GeoTIFF file
        for i in range(1, num_bands + 1):
            # Read the i-th band
            band = src.read(i)
            if i<=9:
            # Define the output file path
                prefix = "S2A_MSIL1C_20230818T100031_N0509_R122_T33TTG_20230818T121434_B0"
                output_file = f"{output_dir}/{prefix}{i}.tif"
            else:
                prefix = "S2A_MSIL1C_20230818T100031_N0509_R122_T33TTG_20230818T121434_B"
                output_file = f"{output_dir}/{prefix}{i}.tif"

            # Define the profile for the output file
            profile = src.profile
            profile.update(count=1)  # Set the count to 1 since we're writing one band

            # Write the band to a new file
            with rasterio.open(output_file, 'w', **profile) as dst:
                dst.write(band, 1)

            print(f"Saved band {i} to {output_file}")

# Example usage
input_file ='/home/aneesha/change_detection/S2A_MSIL1C_20240214T100121_N0510_R122_T33TTG_20240214T104957_bilinear_rome.tif'
output_dir = './output_image_unstacked/'
os.makedirs(output_dir, exist_ok=True)
unstack_bands(input_file, output_dir)
