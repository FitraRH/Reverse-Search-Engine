# Image Search Admin Panel

## Overview
This project implements an **Image Search Admin Panel** using **Selenium** and **Streamlit**. The application allows users to automatically search and download images from Google Image Search or manually upload images to a dataset. The application also supports batch uploads via ZIP files and organizes images into predefined folders.

## Features

1. **Automatic Image Search & Download:**
   - Uses Selenium to search Google Images based on user input.
   - Downloads images directly into categorized folders.

2. **Manual Uploads:**
   - Supports individual image uploads.
   - Allows batch uploads via ZIP files.

3. **Dataset Organization:**
   - Automatically categorizes images into specified folders.
   - Ensures valid file naming conventions.

4. **Admin Panel:**
   - Built using Streamlit, providing a user-friendly web interface for managing datasets.

5. **Logging:**
   - Logs key actions and errors for debugging and transparency.

## Libraries Used

- **os**: For directory and file operations.
- **time**: For generating unique filenames and delays.
- **requests**: For downloading images.
- **logging**: For logging application events.
- **Pillow**: For image processing.
- **selenium**: For web scraping Google Images.
- **webdriver-manager**: For managing ChromeDriver.
- **streamlit**: For creating the admin panel interface.
- **re**: For handling regular expressions in file naming.
- **warnings**: For suppressing unnecessary warnings.
- **shutil**: For handling file and directory operations.
- **pathlib**: For working with file paths.
- **zipfile**: For extracting ZIP files.
- **tempfile**: For creating temporary directories.

## Functions

### 1. **`setup_driver`**

Sets up and configures the Selenium ChromeDriver.

**Key Features:**
- Runs Chrome in headless mode.
- Configures Chrome with various optimizations and workarounds.
- Disables GPU and unnecessary features for stability.

**Output:**
- Returns an instance of a configured Selenium WebDriver.

### 2. **`search_images_selenium`**

Performs Google Image Search and extracts image URLs using Selenium.

**Input:**
- `query`: The search term.
- `num_results`: Number of image URLs to retrieve.

**Output:**
- List of image URLs.

### 3. **`download_image`**

Downloads an image from a URL and saves it to a specified folder.

**Input:**
- `url`: URL of the image.
- `query`: The category or class name for the image.

**Output:**
- Saves the image in the appropriate folder and returns its path.

### 4. **`handle_manual_upload`**

Processes individual image uploads through the admin panel.

**Input:**
- `uploaded_files`: List of uploaded image files.
- `target_folder`: Destination folder for the images.

**Output:**
- Saves the uploaded images to the target folder and returns the paths.

### 5. **`handle_zip_upload`**

Processes ZIP file uploads and extracts images to a specific folder.

**Input:**
- `zip_file`: The uploaded ZIP file.
- `custom_class_name`: Name of the target folder/class.

**Output:**
- Extracts and saves images from the ZIP file into the specified folder.

### 6. **`get_existing_folders`**

Retrieves a list of existing dataset folders.

**Output:**
- List of folder names in the dataset directory.

## Input and Output

### Input

1. **Search Query:**
   - A text query for automatic image search.

2. **Number of Images:**
   - Number of images to retrieve during the automatic search.

3. **Uploaded Files:**
   - Individual image files or a ZIP file for manual uploads.

4. **Folder/Class Name:**
   - Destination folder name for organizing the uploaded images.

### Output

1. **Downloaded Images:**
   - Images retrieved from Google Image Search and saved to folders.

2. **Uploaded Images:**
   - Images uploaded through the manual or ZIP upload process.

3. **Organized Dataset:**
   - All images stored in the `101_ObjectCategories` directory, categorized into folders.

## Setup and Usage

### Prerequisites

1. **Python 3.7+**
2. Install the required libraries:
   ```bash
   pip install selenium webdriver-manager Pillow streamlit requests
   ```

### Running the Application

1. Launch the Streamlit admin panel:
   ```bash
   streamlit run admin_panel.py
   ```
2. Use the tabs to:
   - Perform automatic image search and download.
   - Manually upload individual images or ZIP files.

### Directory Structure

- Dataset directory: `101_ObjectCategories`
- Saved images are organized into subfolders corresponding to class names.

## Conclusion

The Image Search Admin Panel provides a robust and intuitive way to manage datasets through automatic and manual image collection. Its modular design ensures easy extensibility and integration into larger workflows.

