import os
import numpy as np
import torch
from torchvision import models, transforms
from sklearn.metrics.pairwise import cosine_similarity
from PIL import Image
import streamlit as st
import warnings
from torch.utils.data import DataLoader, Dataset
from difflib import get_close_matches

# Suppress deprecation warnings
warnings.filterwarnings("ignore", category=UserWarning, message=".fileUploaderEncoding.")

# Define the directory where the Caltech 101 dataset is stored
dataset_dir = '101_ObjectCategories'
features_file = 'features.npy'
labels_file = 'labels.npy'

# Check if the dataset directory exists
if not os.path.exists(dataset_dir):
    raise FileNotFoundError(f"Dataset not found at {dataset_dir}. Please ensure the path is correct.")

# Get class names from the dataset folder
class_names = sorted(os.listdir(dataset_dir))

# Load pretrained ResNet-50 model
model = models.resnet50(pretrained=True)
model = torch.nn.Sequential(*list(model.children())[:-1])  # Remove last layer
model = model.eval()  # Set model to evaluation mode

# Image transformations for ResNet-50
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Dataset for batch processing
class ImageDataset(Dataset):
    def __init__(self, image_paths, transform):
        self.image_paths = image_paths
        self.transform = transform

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        image_path = self.image_paths[idx]
        image = Image.open(image_path).convert('RGB')
        return self.transform(image), image_path

# Function to extract features in batches
def extract_features_in_batches(image_paths, batch_size=32):
    dataset = ImageDataset(image_paths, transform)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

    features = []
    paths = []
    with torch.no_grad():
        for images, image_paths in dataloader:
            batch_features = model(images).squeeze()
            features.append(batch_features)
            paths.extend(image_paths)

    return torch.cat(features), paths

# Function to check for new data and update features and labels
def update_dataset():
    # Initialize features and labels
    features_matrix = []
    labels_matrix = []
    
    # Iterate through the dataset and collect images
    image_paths = []
    labels = []

    for class_idx, class_name in enumerate(class_names):
        class_folder = os.path.join(dataset_dir, class_name)
        if os.path.isdir(class_folder):
            for image_name in os.listdir(class_folder):
                image_path = os.path.join(class_folder, image_name)
                image_paths.append(image_path)
                labels.append(class_idx)

    # Extract features for all images
    if image_paths:
        features_matrix, _ = extract_features_in_batches(image_paths)
        features_matrix = features_matrix.numpy()
        labels_matrix = np.array(labels)

        # Save updated features and labels
        np.save(features_file, features_matrix)
        np.save(labels_file, labels_matrix)

# Run update_dataset before UI starts
if not os.path.exists(features_file) or not os.path.exists(labels_file):
    with st.spinner("Processing dataset... Please wait. This might take a while."):
        update_dataset()

# Function to extract features for a single image
def extract_features_single(image_path):
    image = Image.open(image_path).convert('RGB')
    image_tensor = transform(image).unsqueeze(0)  # Add batch dimension
    with torch.no_grad():
        features = model(image_tensor).squeeze()
    return features.numpy()

# Function to auto-correct class input
def auto_correct_class_name(input_text, class_names, n=1):
    matches = get_close_matches(input_text, class_names, n=n, cutoff=0.6)
    return matches[0] if matches else input_text

# Function to find similar images
def find_similar_images(query_image_path=None, filter_class=None, top_k=5):
    # Load features and labels
    features_matrix = np.load(features_file)
    labels_matrix = np.load(labels_file)

    # If filter_class is specified, return all images in that class
    if filter_class:
        filter_class = auto_correct_class_name(filter_class.lower(), class_names)
        matching_classes = [cls for cls in class_names if filter_class in cls.lower()]

        if matching_classes:
            similar_images = []
            for class_name in matching_classes:
                class_folder = os.path.join(dataset_dir, class_name)
                image_paths = [os.path.join(class_folder, img) for img in os.listdir(class_folder)]
                for img_path in image_paths:
                    similar_images.append((class_name, 1.0, img_path))  # Return all images in the class
            return similar_images

    # If query_image_path is provided, perform search across all classes
    if query_image_path:
        query_features = extract_features_single(query_image_path).reshape(1, -1)
        similarities = cosine_similarity(query_features, features_matrix)
        similar_indices = np.argsort(similarities[0])[-top_k:][::-1]
        similar_images = []

        for idx in similar_indices:
            class_idx = labels_matrix[int(idx)]
            class_name = class_names[int(class_idx)]
            class_folder = os.path.join(dataset_dir, class_name)
            image_names = os.listdir(class_folder)
            if image_names:
                img_path = os.path.join(class_folder, image_names[int(idx) % len(image_names)])
                similarity_score = similarities[0][int(idx)]
                similar_images.append((class_name, similarity_score, img_path))
        return similar_images
    return []

# Streamlit UI
st.title("Reverse Search Engine")

# Upload image for search
uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])
filter_class = st.text_input("Class Name (Optional)")

# Auto-correct input class name
if filter_class:
    corrected_class = auto_correct_class_name(filter_class, class_names)
    if corrected_class != filter_class:
        st.warning(f"Did you mean: {corrected_class}?")
        filter_class = corrected_class

trigger_search = st.button("Search Images")

query_image_path = None
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)
    query_image_path = os.path.join('images', uploaded_file.name)
    os.makedirs('images', exist_ok=True)  # Ensure images folder exists
    image.save(query_image_path)

if trigger_search:
    if query_image_path or filter_class:
        similar_images = find_similar_images(query_image_path=query_image_path, filter_class=filter_class)
        if similar_images:
            st.write("Search Results:")
            cols = st.columns(4)
            for idx, (class_name, similarity_score, img_path) in enumerate(similar_images):
                col = cols[idx % 4]
                img = Image.open(img_path)
                with col:
                    st.image(img, caption=f"{class_name[:10]}...", use_container_width=True)
        else:
            st.write("No results found.")
    else:
        st.warning("Please upload an image or provide a class name.")

# Sidebar for available classes
st.sidebar.title("Available Classes")
st.sidebar.write(", ".join(sorted(class_names)))
