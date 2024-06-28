import numpy as np
from osgeo import gdal
from sklearn import svm
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import train_test_split

# Load the single-band GeoTIFF image
dataset = gdal.Open('landcover_matera1.tif')
image_data = dataset.ReadAsArray()  # Assuming shape is (height, width)

# Assume class `1` is "built-up area" and others are "landcover"
def create_labels(image_data):
    labels = np.where(image_data == 1, 1, 0)  # 1 for built-up area, 0 for landcover
    return labels

# Create labels based on the criteria
labels = create_labels(image_data)

# Reshape the image to (pixels, 1) since it's a single-band image
height, width = image_data.shape
image_reshaped = image_data.reshape(-1, 1)  # Shape: (pixels, 1)

# Ensure labels match the number of pixels
assert labels.size == image_reshaped.shape[0], "Number of labels must match number of pixels"

# Filter out unlabeled pixels (if any)
valid_indices = labels != -1  # Adjust this condition if there's a specific unlabeled value
X = image_reshaped[valid_indices]
y = labels.flatten()[valid_indices]  # Flatten the labels array to match the shape

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
classified_image_reshaped = np.full(labels.shape, -1)  # Initialize with -1 for unlabeled areas
classified_image_reshaped[valid_indices] = classified_image
classified_image_reshaped = classified_image_reshaped.reshape(height, width)

# Save the classified image (optional)
output_dataset = gdal.GetDriverByName('GTiff').Create('classified_image.tif', width, height, 1, gdal.GDT_Byte)
output_dataset.GetRasterBand(1).WriteArray(classified_image_reshaped)
output_dataset.FlushCache()
output_dataset = None
