#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 18:32:54 2024

@author: aneesha
"""

import geopandas as gpd
from shapely.geometry import Polygon
import pyproj

# Define the center coordinates
center_lat = 41.91676207012941
center_lon = 12.423249863753226

# Convert degrees to meters using pyproj
geod = pyproj.Geod(ellps="WGS84")
side_length_km = 5  # Half side length since 25 km² square has a side length of 5 km

# Calculate the corner coordinates in meters from the center
lon1, lat1, _ = geod.fwd(center_lon, center_lat, 45, side_length_km * 1000)
lon2, lat2, _ = geod.fwd(center_lon, center_lat, 135, side_length_km * 1000)
lon3, lat3, _ = geod.fwd(center_lon, center_lat, 225, side_length_km * 1000)
lon4, lat4, _ = geod.fwd(center_lon, center_lat, 315, side_length_km * 1000)

# Create the square polygon using Shapely
square = Polygon([(lon1, lat1), (lon2, lat2), (lon3, lat3), (lon4, lat4), (lon1, lat1)])

# Create a GeoDataFrame
gdf = gpd.GeoDataFrame({'geometry': [square]}, crs="EPSG:4326")

# Save the new shapefile
gdf.to_file("square_25km2.shp")
