import rasterio
import numpy as np
import matplotlib.pyplot as plt
from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def read_geotiff(image_path):
    with rasterio.open(image_path) as src:
        image = src.read().astype('float32')
        meta = src.meta
    return image, meta

def create_training_data(image, labels, n_samples=100):
    np.random.seed(0)
    samples = []
    labels_list = []
    for label in np.unique(labels):
        if label == 0:  # Skip background or unlabelled data
            continue
        idx = np.where(labels == label)
        idx_samples = np.random.choice(len(idx[0]), min(n_samples, len(idx[0])), replace=False)
        samples.append(image[:, idx[0][idx_samples], idx[1][idx_samples]])
        labels_list.extend([label] * len(idx_samples))
    samples = np.concatenate(samples, axis=1).T
    labels_list = np.array(labels_list)
    return samples, labels_list

def classify_image(image, classifier):
    flat_pixels = image.reshape((image.shape[0], -1)).T
    classified = classifier.predict(flat_pixels)
    return classified.reshape((image.shape[1], image.shape[2]))

def plot_classification(image, title="Classified Image"):
    plt.imshow(image, cmap='tab20')
    plt.title(title)
    plt.colorbar()
    plt.show()

# Paths to the input GeoTIFF files
reference_image_path = 'landcover_matera1.tif'
difference_image_path = 'difference_bu.tif'

# Read the GeoTIFF images
reference_image, meta_reference = read_geotiff(reference_image_path)
difference_image, meta_difference = read_geotiff(difference_image_path)

# Assuming that the training labels are provided as an additional input
# This could be a manually created label map where each class is represented by a unique integer
# For simplicity, let's assume a label map with arbitrary labels for demonstration
# In practice, you would need a real label map based on ground truth data
labels = np.zeros((reference_image.shape[1], reference_image.shape[2]), dtype=int)
labels[100:200, 100:200] = 1  # Class 1
labels[300:400, 300:400] = 2  # Class 2

# Visualize the labels to ensure they are correctly defined
plt.imshow(labels, cmap='tab20')
plt.title("Training Labels")
plt.colorbar()
plt.show()

# Create training data from the reference image and labels
samples, labels_list = create_training_data(reference_image, labels)

# Check the unique classes in the training data
unique_classes = np.unique(labels_list)
print(f"Unique classes in the training data: {unique_classes}")

if len(unique_classes) <= 1:
    raise ValueError("The number of classes has to be greater than one for training an SVM classifier.")

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(samples, labels_list, test_size=0.3, random_state=0)

# Train the SVM classifier
classifier = svm.SVC()
classifier.fit(X_train, y_train)

# Evaluate the classifier
y_pred = classifier.predict(X_test)
print(f"Classification accuracy: {accuracy_score(y_test, y_pred)}")

# Classify the difference image
classified_difference = classify_image(difference_image, classifier)

# Plot the classification results
plot_classification(classified_difference, "Classified Difference Image")

# Save the classified difference image
meta_difference.update(dtype='int32', count=1)
with rasterio.open('classified_difference.tif', 'w', **meta_difference) as dst:
    dst.write(classified_difference.astype('int32'), 1)

print("Classified difference image saved as 'classified_difference.tif'.")
