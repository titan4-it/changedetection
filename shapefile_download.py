#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 18:32:54 2024

@author: aneesha
"""

import geopandas as gpd
from shapely.geometry import Polygon
import pyproj
import numpy as np

# Define the center coordinates
center_lat = 45.47422254134666
center_lon = 9.131265623924751
# rome1 : 41.91676207012941, 12.423249863753226
# rome2: 41.872694016485795, 12.397743093253977
#bardonecccia: 45.08609312102315, 6.713488424535582
#varese : 45.60279577776323, 8.857936880373705 
# milan: center_lat = 45.52073562565231,center_lon = 9.229624544238265 (milan)
# milan2 : 45.47422254134666, 9.131265623924751

# Convert degrees to meters using pyproj
geod = pyproj.Geod(ellps="WGS84")
half_diagonallength_km = 5/np.sqrt(2) # 5/sqrt2 --- gives 5*5 total diagonal length

# Calculate the corner coordinates in meters from the center
lon1, lat1, _ = geod.fwd(center_lon, center_lat, 45, half_diagonallength_km * 1000)
lon2, lat2, _ = geod.fwd(center_lon, center_lat, 135, half_diagonallength_km * 1000)
lon3, lat3, _ = geod.fwd(center_lon, center_lat, 225, half_diagonallength_km * 1000)
lon4, lat4, _ = geod.fwd(center_lon, center_lat, 315, half_diagonallength_km * 1000)

# Create the square polygon using Shapely
square = Polygon([(lon1, lat1), (lon2, lat2), (lon3, lat3), (lon4, lat4), (lon1, lat1)])

# Create a GeoDataFrame
gdf = gpd.GeoDataFrame({'geometry': [square]}, crs="EPSG:4326")

# Save the new shapefile
gdf.to_file("milan2-square_25km2.shp")
