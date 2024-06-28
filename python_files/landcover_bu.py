import numpy as np
import rasterio
import matplotlib.pyplot as plt
from collections import Counter

# Define the label mapping dictionary
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
    13: "Permanently irrigated land",
    14: "Rice fields",
    15: "Vineyards",
    16: "Fruit trees and berry plantations",
    17: "Olive groves",
    18: "Pastures",
    19: "Annual crops associated with permanent crops",
    20: "Complex cultivation patterns",
    21: "Land principally occupied by agriculture, with significant areas of natural vegetation",
    22: "Agro-forestry areas",
    23: "Broad-leaved forest",
    24: "Coniferous forest",
    25: "Mixed forest",
    26: "Natural grasslands",
    27: "Moors and heathland",
    28: "Sclerophyllous vegetation",
    29: "Transitional woodland-shrub",
    30: "Beaches, dunes, sands",
    31: "Bare rocks",
    32: "Sparsely vegetated areas",
    33: "Burnt areas",
    34: "Glaciers and perpetual snow",
    35: "Inland marshes",
    36: "Peat bogs",
    37: "Salt marshes",
    38: "Salines",
    39: "Intertidal flats",
    40: "Water courses",
    41: "Water bodies",
    42: "Coastal lagoons",
    43: "Estuaries",
    44: "Sea and ocean",
    48: "NODATA"
}

# Path to the input image
input_image_path = 'rome_landcover.tif'

# Read the input image
with rasterio.open(input_image_path) as src:
    image_data = src.read(1)  # Read the first band

# Flatten the image data and count the occurrences of each label
flat_data = image_data.flatten()
label_counts = Counter(flat_data)

# Remove the NODATA value (if any)
if 48 in label_counts:
    del label_counts[48]

# Extract labels and their corresponding counts
labels = [label_mapping.get(label, "Unknown") for label in label_counts.keys()]
counts = list(label_counts.values())

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
plt.title('Distribution of Land Cover Types')
plt.tight_layout()

# Show the count plot
plt.show()

# Create a bar graph for the area covered
plt.figure(figsize=(15, 8))
plt.barh(labels, areas, color='skyblue')
plt.xlabel('Area (sq km)')
plt.ylabel('Land Cover Type')
plt.title('Area Covered by Land Cover Types')
plt.tight_layout()

# Show the area plot
plt.show()
