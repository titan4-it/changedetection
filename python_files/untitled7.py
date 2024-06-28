#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 17:35:38 2024

@author: aneesha
"""

import numpy as np
from osgeo import gdal
from sklearn import svm
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import train_test_split

# Load the GeoTIFF image
dataset = gdal.Open('/home/aneesha/change_detection/u2018_clc2018_v2020_20u1_raster100m/DATA/U2018_CLC2018_V2020_20u1.tif')
image_data = dataset.ReadAsArray()  # Assuming shape is (bands, height, width)

# Read labels from the text file
# Assuming the text file has one label per line corresponding to each pixel
labels = np.loadtxt('/home/aneesha/change_detection/u2018_clc2018_v2020_20u1_raster100m/Legend/CLC2018_CLC2018_V2018_20_QGIS.txt', dtype=int)

# Reshape the image to (pixels, bands)
class_labels = []
with open(label_file, 'r') as file:
    for line in file:
        parts = line.split(',')
        class_label = int(parts[0])
        class_labels.append(class_label)
class_labels = np.array(class_labels)

# Reshape the image to (pixels, bands)
num_bands, height, width = image_data.shape
image_reshaped = image_data.reshape(num_bands, -1).T  # Shape: (pixels, num_bands)

# Ensure class labels match the number of pixels
assert class_labels.shape[0] == image_reshaped.shape[0], "Number of class labels must match number of pixels"

# Filter out unlabeled pixels (assuming unlabeled pixels have a specific value, e.g., -1 or 999)
valid_indices = class_labels != 999  # Change this condition based on your unlabeled value
X = image_reshaped[valid_indices]
y = class_labels[valid_indices]

# Split data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train SVM classifier
classifier = make_pipeline(StandardScaler(), svm.SVC(kernel='rbf', C=1, gamma='scale'))
classifier.fit(X_train, y_train)

# Evaluate classifier
y_pred = classifier.predict(X_test)
print(classification_report(y_test, y_pred))
print("Accuracy:", accuracy_score(y_test, y_pred))

# Classify the entire image
classified_image = classifier.predict(image_reshaped)

# Reshape the classified result back to the original image dimensions
classified_image_reshaped = np.full(class_labels.shape, 999)  # Initialize with 999 for unlabeled areas
classified_image_reshaped[valid_indices] = classified_image
classified_image_reshaped = classified_image_reshaped.reshape(height, width)

# Save the classified image (optional)
output_dataset = gdal.GetDriverByName('GTiff').Create('classified_image.tif', width, height, 1, gdal.GDT_Byte)
output_dataset.GetRasterBand(1).WriteArray(classified_image_reshaped)
output_dataset.FlushCache()
output_dataset = None