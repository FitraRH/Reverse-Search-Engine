# Reverse Image Search Engine

## Overview

This project implements a Reverse Image Search Engine using a pre-trained ResNet-50 deep learning model. The system extracts image features and compares them to identify similar images within a dataset (Caltech 101). The project includes a Streamlit-based web interface for user interaction.

## Features

1. **Feature Extraction:** Extracts deep learning-based features from images using ResNet-50.
2. **Batch Processing:** Processes images in batches for efficiency.
3. **Class-Based Search:** Allows searching for images within a specific class.
4. **Similarity Search:** Finds the most similar images based on cosine similarity.
5. **Auto-Correction:** Suggests the correct class name for user-provided input using fuzzy matching.
6. **Streamlit Web Interface:** A user-friendly interface to upload images and view search results.

## Libraries Used

- **os:** For directory and file path operations.
- **numpy:** For numerical operations and matrix manipulation.
- **torch:** For working with deep learning models and tensors.
- **torchvision:** For accessing pre-trained models and image transformations.
- **scikit-learn (cosine\_similarity):** For computing similarity scores.
- **Pillow:** For image manipulation.
- **streamlit:** For creating the web interface.
- **warnings:** For suppressing unnecessary warnings.
- **difflib:** For auto-correcting class names using fuzzy matching.

## Dataset

- The system uses the Caltech 101 dataset, which consists of 101 object categories.
- Directory structure:
  ```
  101_ObjectCategories/
      class_1/
          image_1.jpg
          image_2.jpg
          ...
      class_2/
          ...
  ```

## Input and Output

### Input

1. **Image File:** An uploaded image file (JPEG, PNG).
2. **Class Name (Optional):** A string representing the desired class name for filtering search results.

### Output

1. **Search Results:**
   - Displayed as a grid of images with similarity scores.
   - Images are sourced from the dataset.

## Code Details

### 1. Pre-Trained Model

- **ResNet-50:** A pre-trained deep learning model from torchvision.
- Last classification layer is removed to use the model for feature extraction.
- Input images are resized to 224x224 and normalized.

### 2. Image Transformations

Images are preprocessed using:

- **Resize:** Resizes images to (224x224).
- **ToTensor:** Converts images to PyTorch tensors.
- **Normalize:** Normalizes images with mean and standard deviation values suitable for ResNet-50.

### 3. Batch Processing

- Images are processed in batches to optimize memory usage and computation time.
- **Dataset and DataLoader:** PyTorch utilities for managing datasets and batching.

### 4. Feature Extraction

Features are extracted from images using the ResNet-50 model and saved as NumPy arrays for future use.

### 5. Auto-Correction for Class Names

- Uses the `difflib.get_close_matches` function to suggest corrections for user input.
- Fuzzy matching ensures robust handling of typos or partial matches.

### 6. Cosine Similarity Search

- Compares query image features with dataset features.
- Retrieves the top-k most similar images.

### 7. Streamlit Interface

#### Main Page:

- **Upload Image:** Allows users to upload an image for search.
- **Class Name (Optional):** Input field for filtering search results.
- **Search Button:** Triggers the search functionality.

#### Sidebar:

- Displays a list of all available classes in the dataset.

### Functions

#### 1. `extract_features_in_batches`

Extracts features from a list of image paths in batches.

**Input:**

- `image_paths`: List of image file paths.
- `batch_size`: Number of images to process per batch (default=32).

**Output:**

- Tensor of extracted features.
- List of image paths.

#### 2. `update_dataset`

Processes the dataset to extract features and labels for all images. Saves the data for future use.

#### 3. `extract_features_single`

Extracts features for a single image.

**Input:**

- `image_path`: Path to the image file.

**Output:**

- NumPy array of extracted features.

#### 4. `auto_correct_class_name`

Suggests corrections for user-provided class names.

**Input:**

- `input_text`: User input text.
- `class_names`: List of available class names.

**Output:**

- Corrected class name or the original input.

#### 5. `find_similar_images`

Finds similar images based on cosine similarity or class name filtering.

**Input:**

- `query_image_path`: Path to the query image.
- `filter_class`: Class name for filtering (optional).
- `top_k`: Number of similar images to retrieve (default=5).

**Output:**

- List of tuples containing class name, similarity score, and image path.

## Setup and Usage

### Prerequisites

- Python 3.7+
- Install required libraries using:
  ```bash
  pip install numpy torch torchvision scikit-learn pillow streamlit
  ```

### Running the Application

1. Ensure the dataset (`101_ObjectCategories`) is in the same directory as the script.
2. Start the Streamlit app:
   ```bash
   streamlit run search_engine.py
   ```
3. Upload an image or specify a class name to search for similar images.

## Improvements

- Extend support to other datasets.
- Add advanced filtering options (e.g., by image resolution, color).
- Integrate with cloud storage for larger datasets.
- Improve UI responsiveness and error handling.

## Conclusion

This Reverse Image Search Engine provides a powerful and intuitive way to search for images based on content similarity or class. Its modular design allows easy extension and integration into larger systems.

