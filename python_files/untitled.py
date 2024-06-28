import rasterio
import numpy as np
import matplotlib.pyplot as plt
from rasterio.warp import transform

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

def calculate_bu(masked_image):
    band_4 = masked_image[4]
    band_5 = masked_image[5]
    band_6 = masked_image[6]
    band_8 = masked_image[8]
    band_11 = masked_image[11]
   
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

def extract_pixel_values(image1_path, image2_path, coordinates):
    values_bu1 = []
    values_bu2 = []
    with rasterio.open(image1_path) as src1, rasterio.open(image2_path) as src2:
        for lon, lat in coordinates:
            row1, col1 = src1.index(lon, lat)
            row2, col2 = src2.index(lon, lat)
            
            if row1 is None or col1 is None or row2 is None or col2 is None:
                # Handle case where index is out of bounds
                values_bu1.append(np.nan)
                values_bu2.append(np.nan)
            else:
                # Ensure indices are within bounds
                if 0 <= row1 < src1.height and 0 <= col1 < src1.width:
                    values_bu1.append(src1.read(1)[row1, col1])
                else:
                    values_bu1.append(np.nan)
                
                if 0 <= row2 < src2.height and 0 <= col2 < src2.width:
                    values_bu2.append(src2.read(1)[row2, col2])
                else:
                    values_bu2.append(np.nan)
    return values_bu1, values_bu2

def plot_pixel_values(values_bu1, values_bu2, coordinates):
    plt.figure(figsize=(10, 5))
    indices = np.arange(len(coordinates))
    width = 0.4
    plt.bar(indices - width/2, values_bu1, width=width, label='BU1')
    plt.bar(indices + width/2, values_bu2, width=width, label='BU2')
    plt.xlabel('Coordinate Index')
    plt.ylabel('BU Value')
    plt.title('BU Values at Specified Coordinates')
    plt.xticks(indices, [f'({lon}, {lat})' for lon, lat in coordinates], rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Paths to the input and output files
landcover_image_path = '/home/aneesha/change_detection/rome_landcover_clipped.tif'
image1_path = '/home/aneesha/change_detection/S2A_MSIL1C_20240214T100121_N0510_R122_T33TTG_20240214T104957_bilinear_rome.tif'
image2_path = '/home/aneesha/change_detection/S2A_MSIL1C_20230818T100031_N0509_R122_T33TTG_20230818T121434_bilinear_rome.tif'
output_bu1_path = '/home/aneesha/change_detection/bu_output1.tif'
output_bu2_path = '/home/aneesha/change_detection/bu_output2.tif'

# Coordinates for pixel value extraction (latitude, longitude)
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

# Reproject coordinates to match the CRS of image1 and image2
# Assuming image1 and image2 have the same CRS, use image1's CRS
with rasterio.open(image1_path) as src:
    src_crs = src.crs
    projected_coordinates = reproject_coordinates(coordinates, {'init': 'EPSG:4326'}, src_crs)

# Extract BU values for the specified coordinates
values_bu1, values_bu2 = extract_pixel_values(output_bu1_path, output_bu2_path, projected_coordinates)

# Plot BU values for bu1 and bu2 at the specified coordinates
plot_pixel_values(values_bu1, values_bu2, coordinates)
