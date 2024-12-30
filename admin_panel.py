import os
import time
import requests
import logging
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import streamlit as st
import re
import warnings
import shutil
from pathlib import Path
import zipfile
import tempfile

# Suppress deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="streamlit")

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

# Driver setup function with multiple workarounds
def setup_driver():
    from selenium.webdriver.chrome.options import Options
    
    chrome_options = Options()
    
    # Workarounds for GPU and rendering
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-browser-side-navigation")
    chrome_options.add_argument("--remote-debugging-port=9222")
    
    # Additional options for stability
    chrome_options.page_load_strategy = 'none'
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Headless mode with additional options
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # User agent 
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    try:
        # Driver installation
        service = Service(ChromeDriverManager().install())
        
        # Adding timeout
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(30)  # Timeout 30 second
        
        return driver
    
    except Exception as e:
        logging.error(f"Failed to create WebDriver: {e}")
        raise

# Image search function with comprehensive error handling
def search_images_selenium(query, num_results=20):
    driver = None
    image_urls = []
    
    try:
        driver = setup_driver()
        
        # Encode query for URL
        import urllib.parse
        encoded_query = urllib.parse.quote(query)
        search_url = f"https://www.google.com/search?tbm=isch&q={encoded_query}"
        logging.info(f"Opening URL: {search_url}")
        
        # Open page with error handling
        try:
            driver.get(search_url)
        except Exception as navigation_error:
            logging.warning(f"Failed to navigate to {search_url}: {navigation_error}")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        for _ in range(10): 
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
        
        # Multiple selector for image
        selectors = [
            "img.Q4LuWd", 
            "div[data-ri] img",  
            "img[data-src]",  
            "img[src^='http']" 
        ]
        
        img_elements = []
        for selector in selectors:
            img_elements = driver.find_elements(By.CSS_SELECTOR, selector)
            logging.info(f"Selector {selector} found {len(img_elements)} images")
            
            if img_elements:
                break
        
        # Process image URL
        unique_urls = set() 
        for img in img_elements:
            try:
                # Multi-method extraction URL
                url_methods = [
                    lambda: img.get_attribute('src'),
                    lambda: img.get_attribute('data-src'),
                    lambda: driver.execute_script("return arguments[0].currentSrc", img)
                ]
                
                url = None
                for method in url_methods:
                    try:
                        url = method()
                        if url and url.startswith(('http', 'https', 'data:image')):
                            break
                    except:
                        continue
                
                # Avoid duplicates and ensure valid URLs
                if url and url not in unique_urls:
                    unique_urls.add(url)
                    image_urls.append(url)
                    logging.info(f"Extracted URL: {url}")
                
                # Stop when you have reached the desired amount
                if len(image_urls) >= num_results:
                    break
            
            except Exception as img_error:
                logging.warning(f"Failed to extract image: {img_error}")
            
            if len(image_urls) >= num_results:
                break
    
    except Exception as e:
        logging.error(f"General error: {e}")
    
    finally:
        if driver:
            driver.quit()
    
    return image_urls

# Download image
def download_image(url, query):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # For base64 image
        if url.startswith('data:image'):
            import base64
            header, encoded = url.split(",", 1)
            image_data = base64.b64decode(encoded)
            img = Image.open(BytesIO(image_data))
        else:
            response = requests.get(url, headers=headers, timeout=10)
            img = Image.open(BytesIO(response.content))
        
        # Folder name normalization
        class_name = query.lower().replace(' ', '_')
        class_name = re.sub(r'[^a-z0-9_]', '', class_name)
        
        # Create a folder if it doesn't already exist
        dataset_dir = '101_ObjectCategories'
        class_folder = os.path.join(dataset_dir, class_name)
        os.makedirs(class_folder, exist_ok=True)
        
        # Save image
        filename = f"{int(time.time())}_{hash(url)}.jpg"
        img_path = os.path.join(class_folder, filename)
        img.convert('RGB').save(img_path, 'JPEG')
        
        return img_path
    
    except Exception as e:
        logging.error(f"Failed to download image: {e}")
        return None

# Function to handle manual image upload
def handle_manual_upload(uploaded_files, target_folder):
    saved_paths = []
    
    try:
        # Create dataset directory if it doesn't exist
        dataset_dir = '101_ObjectCategories'
        os.makedirs(dataset_dir, exist_ok=True)
        
        # Create or get target folder
        target_path = os.path.join(dataset_dir, target_folder)
        os.makedirs(target_path, exist_ok=True)
        
        # Process each uploaded file
        for uploaded_file in uploaded_files:
            try:
                # Read image and convert to RGB
                img = Image.open(uploaded_file)
                img = img.convert('RGB')
                
                # Generate unique filename
                filename = f"{int(time.time())}_{hash(uploaded_file.name)}.jpg"
                img_path = os.path.join(target_path, filename)
                
                # Save image
                img.save(img_path, 'JPEG')
                saved_paths.append(img_path)
                logging.info(f"Successfully saved image: {img_path}")
                
            except Exception as e:
                logging.error(f"Failed to process file {uploaded_file.name}: {e}")
                continue
                
        return saved_paths
    
    except Exception as e:
        logging.error(f"Failed to handle manual upload: {e}")
        return []

# Function to handle ZIP file upload and extraction with custom folder name
def handle_zip_upload(zip_file, custom_class_name):
    saved_paths = []
    
    try:
        # Create dataset directory if it doesn't exist
        dataset_dir = '101_ObjectCategories'
        os.makedirs(dataset_dir, exist_ok=True)
        
        # Use custom class name as target folder
        target_folder = custom_class_name.lower().replace(' ', '_')
        target_folder = re.sub(r'[^a-z0-9_]', '', target_folder)
        target_path = os.path.join(dataset_dir, target_folder)
        os.makedirs(target_path, exist_ok=True)
        
        # Create a temporary directory to extract ZIP contents
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save the uploaded ZIP file temporarily
            temp_zip_path = os.path.join(temp_dir, 'upload.zip')
            with open(temp_zip_path, 'wb') as f:
                f.write(zip_file.getbuffer())
            
            # Extract the ZIP file
            with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Process all images in the extracted contents
            valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in valid_extensions):
                        try:
                            # Open and process image
                            img_path = os.path.join(root, file)
                            img = Image.open(img_path)
                            img = img.convert('RGB')
                            
                            # Generate unique filename
                            filename = f"{int(time.time())}_{hash(file)}.jpg"
                            save_path = os.path.join(target_path, filename)
                            
                            # Save image
                            img.save(save_path, 'JPEG')
                            saved_paths.append(save_path)
                            logging.info(f"Successfully saved image from ZIP: {save_path}")
                            
                        except Exception as e:
                            logging.error(f"Failed to process file {file} from ZIP: {e}")
                            continue
    
    except Exception as e:
        logging.error(f"Failed to handle ZIP upload: {e}")
        
    return saved_paths

# Function to get existing folders
def get_existing_folders():
    dataset_dir = '101_ObjectCategories'
    if not os.path.exists(dataset_dir):
        os.makedirs(dataset_dir)
    return [d for d in os.listdir(dataset_dir) if os.path.isdir(os.path.join(dataset_dir, d))]

# Streamlit UI
st.title("Admin Panel")

# Create tabs for different functionalities
tab1, tab2 = st.tabs(["Auto Search & Download", "Manual Upload"])

# Tab 1: Auto Search & Download
with tab1:
    query = st.text_input("Enter search keyword", "")
    num_images = st.slider("Number of images to download", min_value=10, max_value=50, value=20)
    
    if st.button("Search and Download Images"):
        if query:
            st.write(f"Searching for images related to '{query}'...")
            
            try:
                image_urls = search_images_selenium(query, num_results=num_images)
                
                if image_urls:
                    st.write(f"Found {len(image_urls)} image URLs. Downloading...")

                    saved_images = []
                    progress_bar = st.progress(0)
                    
                    for i, url in enumerate(image_urls):
                        img_path = download_image(url, query)
                        if img_path:
                            saved_images.append(img_path)
                        
                        progress_bar.progress((i + 1) / len(image_urls))
                    
                    if saved_images:
                        st.write(f"Successfully downloaded {len(saved_images)} images!")
                        
                        # Show images in a grid
                        cols = st.columns(5)  # 5 columns
                        for i, img_path in enumerate(saved_images):
                            cols[i % 5].image(img_path, caption=f"Image {i+1}", use_container_width=True)
                    else:
                        st.write("No images were downloaded.")
                else:
                    st.write("No images found for the given query.")
            
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.write("Please enter a search query.")

# Tab 2: Manual Upload
with tab2:
    # Get existing folders
    existing_folders = get_existing_folders()
    
    # Radio button to choose between existing or new folder
    folder_choice = st.radio(
        "Choose destination folder",
        ["Use existing folder", "Create new folder"]
    )
    
    if folder_choice == "Use existing folder":
        if existing_folders:
            target_folder = st.selectbox("Select destination folder", existing_folders)
        else:
            st.warning("No existing folders found. Please create a new folder.")
            target_folder = None
    else:
        new_folder = st.text_input("Enter new folder name")
        if new_folder:
            target_folder = new_folder.lower().replace(' ', '_')
            target_folder = re.sub(r'[^a-z0-9_]', '', target_folder)
        else:
            target_folder = None
    
    # Add upload type selection
    upload_type = st.radio("Choose upload type", ["Individual Images", "ZIP File"])
    
    if upload_type == "Individual Images":
        # Existing file uploader for individual images
        uploaded_files = st.file_uploader(
            "Choose image files",
            type=['png', 'jpg', 'jpeg', 'gif', 'bmp'],
            accept_multiple_files=True
        )
        
        if st.button("Upload Images") and uploaded_files and target_folder:
            st.write("Uploading images...")
            try:
                saved_paths = handle_manual_upload(uploaded_files, target_folder)
                if saved_paths:
                    st.write(f"Successfully uploaded {len(saved_paths)} images to folder '{target_folder}'!")
                    cols = st.columns(5)
                    for i, img_path in enumerate(saved_paths):
                        cols[i % 5].image(img_path, caption=f"Image {i+1}", use_container_width=True)
                else:
                    st.warning("No images were uploaded successfully.")
            except Exception as e:
                st.error(f"An error occurred during upload: {e}")
    
    else:  # ZIP File upload
        # Add text input to specify the folder class name
        custom_class_name = st.text_input("Enter class name for the ZIP content")

        uploaded_zip = st.file_uploader(
            "Choose ZIP file containing images",
            type=['zip'],
            accept_multiple_files=False
        )
        
        # Check that the folder class name is filled in
        if st.button("Upload ZIP") and uploaded_zip and custom_class_name:
            st.write("Processing ZIP file...")
            try:
                # Call the handle_zip_upload function with custom_class_name
                saved_paths = handle_zip_upload(uploaded_zip, custom_class_name)
                if saved_paths:
                    st.write(f"Successfully extracted and processed {len(saved_paths)} images from ZIP to folder '{custom_class_name}'!")
                    cols = st.columns(5)
                    for i, img_path in enumerate(saved_paths):
                        cols[i % 5].image(img_path, caption=f"Image {i+1}", use_container_width=True)
                else:
                    st.warning("No images were extracted from the ZIP file.")
            except Exception as e:
                st.error(f"An error occurred during ZIP processing: {e}")
        
        # Validate input if the folder class name has not been filled
        elif not custom_class_name:
            st.warning("Please enter a class name for the ZIP content.")
        elif not uploaded_zip:
            st.warning("Please select a ZIP file to upload.")
