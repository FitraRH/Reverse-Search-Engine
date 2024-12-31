import os
import time
import requests
import logging
import json
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import re
import warnings
import shutil
from pathlib import Path
import zipfile
import tempfile
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import base64

# Suppress deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

app = Flask(__name__)

# Configure upload folder
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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
    chrome_options.page_load_strategy = 'normal'
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Headless mode with additional options
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # User agent 
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    try:
        # Driver installation
        service = Service(ChromeDriverManager().install())
        
        # Adding timeout
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(30)  # Timeout 30 seconds
        
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

# API Routes

@app.route('/api/search', methods=['POST'])
def search_images():
    try:
        if request.is_json:
            data = request.get_json()
            query = data.get('query')
            num_images = data.get('num_images', 20)
        else:
            query = request.form.get('query')
            num_images = request.form.get('num_images', 20)
        
        if not query:
            return jsonify({'error': 'Query parameter is required'}), 400
        
        image_urls = search_images_selenium(query, num_results=int(num_images))
        
        if not image_urls:
            return jsonify({'error': 'No images found'}), 404
        
        saved_images = []
        for url in image_urls:
            img_path = download_image(url, query)
            if img_path:
                saved_images.append(img_path)
        
        return jsonify({
            'message': f'Successfully downloaded {len(saved_images)} images',
            'saved_images': saved_images
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload/images', methods=['POST'])
def upload_images():
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
            
        files = request.files.getlist('files')
        target_folder = request.form.get('target_folder')
        
        if not target_folder:
            return jsonify({'error': 'Target folder is required'}), 400
            
        saved_paths = handle_manual_upload(files, target_folder)
        
        if not saved_paths:
            return jsonify({'error': 'No images were saved'}), 400
            
        return jsonify({
            'message': f'Successfully uploaded {len(saved_paths)} images',
            'saved_paths': saved_paths
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload/zip', methods=['POST'])
def upload_zip():
    try:
        if 'zip_file' not in request.files:
            return jsonify({'error': 'No ZIP file provided'}), 400
            
        zip_file = request.files['zip_file']
        custom_class_name = request.form.get('custom_class_name')
        
        if not custom_class_name:
            return jsonify({'error': 'Custom class name is required'}), 400
            
        if not zip_file.filename.endswith('.zip'):
            return jsonify({'error': 'File must be a ZIP archive'}), 400
            
        saved_paths = handle_zip_upload(zip_file, custom_class_name)
        
        if not saved_paths:
            return jsonify({'error': 'No images were extracted from the ZIP file'}), 400
            
        return jsonify({
            'message': f'Successfully extracted {len(saved_paths)} images',
            'saved_paths': saved_paths
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/folders', methods=['GET'])
def list_folders():
    try:
        folders = get_existing_folders()
        return jsonify({
            'folders': folders
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def home():
    return jsonify({
        'message': 'Welcome to the Image API!',
        'endpoints': {
            '/api/search': 'Search and download images (POST)',
            '/api/upload/images': 'Upload individual images (POST)',
            '/api/upload/zip': 'Upload and extract ZIP images (POST)',
            '/api/folders': 'List existing folders (GET)'
        }
    }), 200

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('101_ObjectCategories', exist_ok=True)
    os.makedirs('uploads', exist_ok=True)

    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
