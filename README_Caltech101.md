# Caltech101 Dataset Setup for PyTorch ResNet50

## Dataset Description

Caltech101 is a dataset consisting of images belonging to 101 different categories. It is commonly used for image classification tasks.

- Number of categories: 101 + 1 (background category)
- Total images: approximately 9,000
- Image format: JPEG
- Image size: variable

## Requirements

```python
pip install torch torchvision numpy Pillow requests tqdm
```

## How to Download the Dataset

### Method 1: Using torchvision

```python
from torchvision.datasets import Caltech101
import torchvision.transforms as transforms

# Define basic transformations
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                       std=[0.229, 0.224, 0.225])
])

# Download dataset (will automatically save to './data' folder)
train_dataset = Caltech101(root='./data',
                          download=True,
                          transform=transform)
```

### Method 2: Manual Download

1. Visit the official Caltech101 website: http://www.vision.caltech.edu/Image_Datasets/Caltech101/
2. Download the `101_ObjectCategories.tar.gz` file
3. Extract the file using:
   ```bash
   tar -xzf 101_ObjectCategories.tar.gz
   ```

## Folder Structure

After downloading and extracting, the folder structure will look like this:

```
data/
└── caltech101/
    └── 101_ObjectCategories/
        ├── accordion/
        ├── airplanes/
        ├── anchor/
        └── ...
```

## Setting up Data Loaders

```python
import torch
from torch.utils.data import DataLoader
from torchvision.datasets import Caltech101
import torchvision.transforms as transforms

def get_data_loaders(batch_size=32):
    # Training transformations
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                           std=[0.229, 0.224, 0.225])
    ])
    
    # Load dataset
    dataset = Caltech101(root='./data',
                        download=True,
                        transform=transform)
    
    # Split dataset (80% training, 20% validation)
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(
        dataset, [train_size, val_size]
    )
    
    # Create data loaders
    train_loader = DataLoader(train_dataset,
                            batch_size=batch_size,
                            shuffle=True,
                            num_workers=4)
    
    val_loader = DataLoader(val_dataset,
                           batch_size=batch_size,
                           shuffle=False,
                           num_workers=4)
    
    return train_loader, val_loader
```

## Using with ResNet50

```python
import torch
import torchvision.models as models

# Load pre-trained ResNet50
model = models.resnet50(pretrained=True)

# Modify the final layer for 101 classes
num_ftrs = model.fc.in_features
model.fc = torch.nn.Linear(num_ftrs, 101)

# Move model to GPU if available
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
model = model.to(device)
```

## Important Notes

1. Ensure you have sufficient disk space (~200MB for the dataset)
2. Make sure you have a stable internet connection for downloading
3. The dataset download might take several minutes depending on your connection speed
4. Consider using GPU acceleration for training, as ResNet50 is a deep model

## Troubleshooting

If you encounter any issues:

1. Check your Python environment and ensure all dependencies are correctly installed
2. Verify that you have sufficient disk space
3. If the automatic download fails, try the manual download method
4. For CUDA out of memory errors, reduce the batch size

