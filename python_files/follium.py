import numpy as np
import rasterio
import folium

# Path to the input image
input_image_path = 'rome_landcover.tif'

# Read the input image
with rasterio.open(input_image_path) as src:
    image_data = src.read(1)  # Read the first band
    bounds = src.bounds  # Get the bounds of the image

# Define colors for the georeferenced map, using transparency for other values
colors = [
    '#ff0000', '#ff5555', '#ffaaaa', '#ff00ff', '#5500ff', 
    '#00ff00', '#00ff55', '#55ff00', '#0055ff', '#0055aa', 
    '#aa00ff', '#00ffaa', '#55ffaa'
]
transparent_color = (0, 0, 0, 0)  # Transparent color for other values

# Create RGBA color mapping
color_mapping = {i: colors[i-1] for i in range(1, 14)}

# Define a function to map the pixel values to RGBA colors
def value_to_rgba(value):
    if value in color_mapping:
        color_hex = color_mapping[value]
        color_rgb = tuple(int(color_hex[i:i+2], 16) for i in (1, 3, 5))
        return color_rgb + (255,)  # Add full opacity
    else:
        return transparent_color

# Convert the image data to RGBA
rgba_data = np.zeros((image_data.shape[0], image_data.shape[1], 4), dtype=np.uint8)
for i in range(image_data.shape[0]):
    for j in range(image_data.shape[1]):
        rgba_data[i, j] = value_to_rgba(image_data[i, j])

# Create a folium map centered around Rome
map_center = [41.9028, 12.4964]  # Latitude and longitude of Rome
m = folium.Map(location=map_center, zoom_start=12)

# Add the OpenStreetMap basemap
folium.TileLayer('cartodbpositron').add_to(m)

# Add the filtered data to the folium map as an ImageOverlay
folium.raster_layers.ImageOverlay(
    image=rgba_data,
    bounds=[[bounds.bottom, bounds.left], [bounds.top, bounds.right]],
    opacity=0.6,  # Adjust opacity to see through to the basemap
    name='Filtered Landcover Overlay',
).add_to(m)

# Highlight the bounds of the image with a red rectangle
folium.vector_layers.Rectangle(
    bounds=[[bounds.bottom, bounds.left], [bounds.top, bounds.right]],
    color='red',
    fill=False,
).add_to(m)

# Add layer control to toggle layers
folium.LayerControl().add_to(m)

# Save the map to an HTML file
m.save('rome_landcover_map_with_bounds.html')

print("Map has been created and saved as 'rome_landcover_map_with_bounds.html'.")
