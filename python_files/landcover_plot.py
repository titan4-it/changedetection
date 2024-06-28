#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 11:16:40 2024

@author: aneesha
"""

import numpy as np
import rasterio
import matplotlib.pyplot as plt
from collections import Counter
from matplotlib.colors import ListedColormap

# Define the label mapping dictionary for values 1 to 13
label_mapping = {
    1: "Continuous urban fabric",
    2: "Discontinuous urban fabric",
    3: "Industrial or commercial units",
    4: "Road and rail networks and associated land",
    5: "Port areas",
    6: "Airports",
    7: "Mineral extraction sites",
    8: "Dump sites",
    9: "Construction sites",
    10: "Green urban areas",
    11: "Sport and leisure facilities",
    12: "Non-irrigated arable land",
    13: "Permanently irrigated land"
}

# Path to the input image
input_image_path = 'rome_landcover.tif'

# Read the input image
with rasterio.open(input_image_path) as src:
    image_data = src.read(1)  # Read the first band

# Filter the image data to include only values 1 to 13
filtered_data = np.where(np.isin(image_data, list(label_mapping.keys())), image_data, 0)

# Flatten the filtered image data and count the occurrences of each label
flat_data = filtered_data.flatten()
label_counts = Counter(flat_data)

# Extract labels and their corresponding counts for values 1 to 13
labels = [label_mapping.get(label, "Unknown") for label in label_counts.keys() if label in label_mapping]
counts = [count for label, count in label_counts.items() if label in label_mapping]

# Calculate the area covered by each land cover type
pixel_size = 25 / 1000  # Assuming 25m x 25m pixels (25 km^2 area)
area_per_pixel = pixel_size * pixel_size
areas = [count * area_per_pixel for count in counts]

# Print unique values and their counts
print("Unique values and their counts:")
for label, count in zip(labels, counts):
    print(f"{label}: {count}")

# Create a bar graph for the counts
plt.figure(figsize=(15, 8))
plt.barh(labels, counts, color='skyblue')
plt.xlabel('Count')
plt.ylabel('Land Cover Type')
plt.title('Distribution of Land Cover Types (Values 1 to 13)')
plt.tight_layout()

# Show the count plot
plt.show()

# Create a bar graph for the area covered
plt.figure(figsize=(15, 8))
plt.barh(labels, areas, color='skyblue')
plt.xlabel('Area (sq km)')
plt.ylabel('Land Cover Type')
plt.title('Area Covered by Land Cover Types (Values 1 to 13)')
plt.tight_layout()

# Show the area plot
plt.show()

# Define colors for the georeferenced map, using transparency for other values
cmap = ListedColormap([
    '#ff0000', '#ff5555', '#ffaaaa', '#ff00ff', '#5500ff', 
    '#00ff00', '#00ff55', '#55ff00', '#0055ff', '#0055aa', 
    '#aa00ff', '#00ffaa', '#55ffaa', '#00000000'  # Adding transparency
])

# Plot the georeferenced map
plt.figure(figsize=(10, 10))
plt.imshow(filtered_data, cmap=cmap)
plt.colorbar(ticks=range(1, 14), label='Land Cover Type')
plt.title('Georeferenced Map of Land Cover Types (Values 1 to 13)')
plt.show()
