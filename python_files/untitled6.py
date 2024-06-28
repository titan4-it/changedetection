#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 17:31:04 2024

@author: aneesha
"""

import numpy as np
from osgeo import gdal
from sklearn import svm
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import classification_report, accuracy_score

# Load the GeoTIFF image
dataset = gdal.Open('/home/aneesha/change_detection/u2018_clc2018_v2020_20u1_raster100m/DATA/U2018_CLC2018_V2020_20u1.tif')
image_data = dataset.ReadAsArray()  # Assuming shape is (bands, height, width)

# Reshape the image to (pixels, bands)
num_bands, height, width = image_data.shape
image_reshaped = image_data.reshape(num_bands, -1).T

# Load labels for training (should be in the same pixel order)
labels = np.load('path_to_labels.npy')

# Split data into training and test sets
# (Use your preferred method for splitting; here we assume a simple split)
train_indices = np.random.choice(len(labels), size=int(0.8 * len(labels)), replace=False)
test_indices = np.setdiff1d(np.arange(len(labels)), train_indices)

X_train = image_reshaped[train_indices]
y_train = labels[train_indices]
X_test = image_reshaped[test_indices]
y_test = labels[test_indices]

# Train SVM classifier
classifier = make_pipeline(StandardScaler(), svm.SVC(kernel='rbf', C=1, gamma='scale'))
classifier.fit(X_train, y_train)

# Evaluate classifier
y_pred = classifier.predict(X_test)
print(classification_report(y_test, y_pred))
print("Accuracy:", accuracy_score(y_test, y_pred))

# Classify the entire image
classified_image = classifier.predict(image_reshaped)
classified_image_reshaped = classified_image.reshape(height, width)

# Save the classified image (optional)
output_dataset = gdal.GetDriverByName('GTiff').Create('classified_image.tif', width, height, 1, gdal.GDT_Byte)
output_dataset.GetRasterBand(1).WriteArray(classified_image_reshaped)
output_dataset.FlushCache()
output_dataset = None
