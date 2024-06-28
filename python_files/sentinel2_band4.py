#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 20 17:26:27 2024

@author: aneesha
"""

#code for requesting all bands for for multiple days (multiple timestamp) for ROME
import datetime
import matplotlib.pyplot as plt
import numpy as np


from sentinelhub import (
    SHConfig,
    CRS,
    BBox,
    DataCollection,
    DownloadRequest,
    MimeType,
    MosaickingOrder,
    SentinelHubDownloadClient,
    SentinelHubRequest,
    bbox_to_dimensions,
)

# Step 1: Set up your configuration
config = SHConfig()
config.sh_client_id = 'sh-f4a2dffd-e52c-4d3b-9e5b-e1a2787df9b6'  # Replace with your Sentinel Hub client ID
config.sh_client_secret = 'hUZYxAyDlH9WEb3GTnLvowHkJLnBkios'  # Replace with your Sentinel Hub client secret
config.sh_token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
config.sh_base_url = "https://sh.dataspace.copernicus.eu"


#betsiboka_coords_wgs84 = (46.16, -16.15, 46.51, -15.58)
betsiboka_coords_wgs84 = ( 12.35,41.839,12.45,41.939)  #rome
#betsiboka_coords_wgs84 = ( -55.391630872035215,71.12790076807497,-53.068787014385705,72.07307624288935)   #greenland
#betsiboka_coords_wgs84 = (12.268432,41.779173,12.641968,42.036864) #La Clapière
resolution = 10
betsiboka_bbox = BBox(bbox=betsiboka_coords_wgs84, crs=CRS.WGS84)
betsiboka_size = bbox_to_dimensions(betsiboka_bbox, resolution=resolution)

print(f"Image shape at {resolution} m resolution: {betsiboka_size} pixels")


start = datetime.datetime(2023, 1, 1)
end = datetime.datetime(2023, 12, 30)
n_chunks = 13
tdelta = (end - start) / n_chunks
edges = [(start + i * tdelta).date().isoformat() for i in range(n_chunks)]
slots = [(edges[i], edges[i + 1]) for i in range(len(edges) - 1)]

print("Monthly time windows:\n")
for slot in slots:
    print(slot)
evalscript_true_color = """
    //VERSION=3

    function setup() {
        return {
            input: [{
                bands: ["B01", "B02", "B03" , "B04", "B05", "B06", "B07", "B08", "B11", "B12",]
            }],
            output: {
                bands: 10
            }
        };
    }

    function evaluatePixel(sample) {
        return [ sample.B01,  sample.B02,  sample.B03,  sample.B04,  sample.B05,  sample.B06,  sample.B07, sample.B08, sample.B11,  sample.B12];
    }
"""

request_true_color = SentinelHubRequest(
    data_folder='test_dir',
    evalscript=evalscript_true_color,
    input_data=[
        SentinelHubRequest.input_data(
            data_collection=DataCollection.SENTINEL2_L1C.define_from(
                "s2l1c", service_url=config.sh_base_url
            ),
            time_interval=("2023-01-01", "2023-12-31"),
        )
    ],
    responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
    bbox=betsiboka_bbox,
    size=betsiboka_size,
    config=config,
)
def get_true_color_request(time_interval):
    return SentinelHubRequest(
        data_folder="test_dir",
        evalscript=evalscript_true_color,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L1C.define_from(
                    "s2l1c", service_url=config.sh_base_url
                ),
                time_interval=time_interval,
            )
        ],
        responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
        bbox=betsiboka_bbox,
        size=betsiboka_size,
        config=config,
    )
# create a list of requests
list_of_requests = [get_true_color_request(slot).get_data(save_data=True) for slot in slots]