import rasterio
from pyproj import Transformer
import numpy as np
import folium
import matplotlib.pyplot as plt

def get_pixel_value(image_path, lat, lon):
    with rasterio.open(image_path) as src:
        # Transform geographic coordinates to image coordinates
        transformer = Transformer.from_crs("EPSG:4326", src.crs, always_xy=True)
        x, y = transformer.transform(lon, lat)
        
        # Get pixel values at the transformed coordinates
        row, col = src.index(x, y)
        pixel_value = src.read(1)[row, col]
        
        return pixel_value

# List of geographic coordinates (latitude, longitude) pairs
coordinates = [
    (41.91638085797895, 12.423027274073522),
    (41.91657450073516, 12.42212071335914),
    (41.9156903193817, 12.422270917060224),
    (41.91588392221169, 12.42282881653152),
    (41.915129466623036, 12.422295056939985),
    (41.914959812684955, 12.424164556610625),
    (41.915171381055956, 12.424864613158745),
    (41.91573822115919, 12.401223623062545),
    (41.90583775468933, 12.401352369094383),
    (41.91765426311034, 12.430534802977597),
]

# Paths to the input GeoTIFF files
image1_path = 'S2A_MSIL1C_20240214T100121_N0510_R122_T33TTG_20240214T104957_bilinear_rome_bu.tif'
image2_path = 'S2A_MSIL1C_20230818T100031_N0509_R122_T33TTG_20230818T121434_bilinear_rome_bu.tif'

# Store the results
results = []

# Iterate over the list of coordinates and compute pixel values
for lat, lon in coordinates:
    pixel_value_image1 = get_pixel_value(image1_path, lat, lon)
    pixel_value_image2 = get_pixel_value(image2_path, lat, lon)
    
    mean = ((pixel_value_image1) + (pixel_value_image2)) / 2 
    diff = (np.abs(pixel_value_image1) - np.abs(pixel_value_image2))
    
    results.append((lat, lon, mean, diff, pixel_value_image1, pixel_value_image2))

# Convert results to a NumPy array for easy manipulation
results = np.array(results)

# Extract data for plotting

latitudes = results[:, 0]
longitudes = results[:, 1]
pixel_values_image1 = results[:, 4].astype(float)
pixel_values_image2 = results[:, 5].astype(float)
means = results[:, 2].astype(float)
diffs = results[:, 3].astype(float)
# Initialize a Folium map centered around the average latitude and longitude
center_lat = np.mean(latitudes)
center_lon = np.mean(longitudes)
mymap = folium.Map(location=[center_lat, center_lon], zoom_start=13)

# Add markers for each coordinate
for i, (lat, lon, mean, diff) in enumerate(zip(latitudes, longitudes, means, diffs)):
    folium.Marker(
        location=[lat, lon],
        popup=f"Mean: {mean:.2f}, Diff: {diff:.2f}",
        tooltip=f"Location {i+1}"
    ).add_to(mymap)

# Save the map to an HTML file
mymap.save("pixel_values_map.html")

# Display the map in Jupyter notebook (if applicable)
# from IPython.display import display
# display(mymap)

# Plot line graphs
plt.figure(figsize=(12, 6))
plt.plot(range(len(coordinates)), means, marker='s', linestyle='-', color='purple', label='Mean Pixel Values')
plt.plot(range(len(coordinates)), diffs, marker='d', linestyle='-', color='red', label='Difference of Pixel Values')
plt.plot(range(len(coordinates)), pixel_values_image1, marker='o', linestyle='-', color='blue', label='Image 1 Pixel Values')
plt.plot(range(len(coordinates)), pixel_values_image2, marker='x', linestyle='--', color='green', label='Image 2 Pixel Values')
plt.xticks(range(len(coordinates)), [f"({lat:.2f}, {lon:.2f})" for lat, lon in coordinates], rotation=45)
plt.xlabel('Coordinate Index')
plt.ylabel('Value')
plt.legend()
plt.title('Mean and Difference of Pixel Values Across Coordinates')
plt.tight_layout()
plt.show()
