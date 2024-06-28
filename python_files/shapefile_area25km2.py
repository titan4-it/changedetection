#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 18:32:54 2024

@author: aneesha
"""

import geopandas as gpd
from shapely.geometry import Polygon, Point
from pyproj import CRS

# Area of the shapefile in square kilometers
area = 25.0
center_lat = 45.08607607721532
center_lon = 6.713542068715514
# Center coordinates (longitude, latitude)
center_coords = (center_lon, center_lat)  # Replace with actual coordinates
area_m2 = area * 10**6  # Convert km² to m²
# Create a Polygon centered at the given coordinates
center_point = Point(center_coords)
half_side_length = (area_m2 ** 0.5) / 2.0  # Side length of the square in meters
half_side_degrees = half_side_length / 111000.0  # Approx. length of 1 degree in meters

# Define the vertices of the square Polygon
vertices = [
    (center_coords[0] - half_side_degrees, center_coords[1] - half_side_degrees),
    (center_coords[0] + half_side_degrees, center_coords[1] - half_side_degrees),
    (center_coords[0] + half_side_degrees, center_coords[1] + half_side_degrees),
    (center_coords[0] - half_side_degrees, center_coords[1] + half_side_degrees),
    (center_coords[0] - half_side_degrees, center_coords[1] - half_side_degrees)  # Closing the polygon
]

# Create the Polygon geometry
polygon_geom = Polygon(vertices)
# Create a GeoDataFrame
crs = CRS.from_epsg(4326)  # WGS84 coordinate system
gdf = gpd.GeoDataFrame(geometry=[polygon_geom], crs=crs)

# Define the filename for the shapefile
output_shapefile = 'area_shapefile.shp'

# Save the GeoDataFrame as a shapefile
gdf.to_file(output_shapefile)
