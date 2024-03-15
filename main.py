import os
from flask import Flask, send_file, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from threading import Thread
import base64
import io
import glob

app = Flask(__name__)

# Define the directory path of app.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
DOWNLOAD_N_DIR = os.path.join(BASE_DIR, "n_images_downloads")
last_image_path = None
last_N_image_path = None

def get_last_file(directory):
    if not os.path.isdir(directory):
        raise ValueError("Directory does not exist.")
    list_of_files = glob.glob(os.path.join(directory, '*'))

    if not list_of_files:
        return None

    latest_file = max(list_of_files, key=os.path.getmtime)
    return latest_file

def download_image():
    global last_image_path
    try:
        # Ensure that the download directory exists
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        
        # Configure ChromeOptions
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        # Set download directory preference
        prefs = {"download.default_directory": DOWNLOAD_DIR}
        chrome_options.add_experimental_option("prefs", prefs)

        # Create WebDriver instance
        driver = webdriver.Chrome(options=chrome_options)

        # Navigate to the website
        driver.get('https://jardimprocedural.netlify.app')

        # Find and click the select element
        select_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'label_control_01'))
        )
        select_element.click()

        # Wait for the generate button to appear and click it
        generate_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'btn1'))
        )
        generate_button.click()

        time.sleep(30)

        # Wait for the download button to appear and click it
        download_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.ID, 'download'))
        )
        download_button.click()

        # Sleep for 5 seconds to ensure all downloads are complete
        time.sleep(5)

        # Get the list of files in the download directory
        downloaded_files = os.listdir(DOWNLOAD_DIR)

        # Filter the list to find the image file
        image_files = [file for file in downloaded_files if file.endswith('.png')]

        # Check if there are image files
        if image_files:
            # Sort the image files by name
            sorted_image_files = sorted(image_files)

            # Get the file name of the downloaded image
            last_image_path = os.path.join(DOWNLOAD_DIR, sorted_image_files[-1])

        # Close the browser
        driver.quit()
    except Exception as e:
        print("Error downloading image:", e)

def download_N_image():
    global last_N_image_path
    try:
        # Ensure that the download directory exists
        os.makedirs(DOWNLOAD_N_DIR, exist_ok=True)
        
        # Configure ChromeOptions
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        # Set download directory preference
        prefs = {"download.default_directory": DOWNLOAD_N_DIR}
        chrome_options.add_experimental_option("prefs", prefs)

        # Create WebDriver instance
        driver = webdriver.Chrome(options=chrome_options)

        # Navigate to the website
        driver.get('https://jardimprocedural.netlify.app')

        # Find and click the select element
        select_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'label_control_02'))
        )
        select_element.click()

        # Wait for the generate button to appear and click it
        generate_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'btn1'))
        )
        generate_button.click()

        time.sleep(300)

        # Wait for the download button to appear and click it
        download_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.ID, 'download'))
        )
        download_button.click()

        # Sleep for 5 seconds to ensure all downloads are complete
        time.sleep(5)

        # Get the list of files in the download directory
        downloaded_files = os.listdir(DOWNLOAD_N_DIR)

        # Filter the list to find the image file
        image_files = [file for file in downloaded_files if file.endswith('.png')]

        # Check if there are image files
        if image_files:
            # Sort the image files by name
            sorted_image_files = sorted(image_files)

            # Get the file name of the downloaded image
            last_N_image_path = os.path.join(DOWNLOAD_N_DIR, sorted_image_files[-1])

        # Close the browser
        driver.quit()
    except Exception as e:
        print("Error downloading image:", e)

def remove_old_files(dirName):
    if not os.path.exists(dirName):
        os.makedirs(dirName)
        
    for filename in os.listdir(dirName):
        file_path = os.path.join(dirName, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print("Error deleting {}: {}".format(file_path, e))

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/download_image', methods=['GET'])
def start_download_image():
    remove_old_files(DOWNLOAD_DIR)
            
    # Start the download process in a separate thread
    Thread(target=download_image).start()
    return jsonify({'message': 'Image download started.'}), 200

@app.route('/download_n_image', methods=['GET'])
def start_download_N_image():
    remove_old_files(DOWNLOAD_N_DIR)
            
    # Start the download process in a separate thread
    Thread(target=download_N_image).start()
    return jsonify({'message': 'Image download started.'}), 200

@app.route('/last_image', methods=['GET'])
def get_last_image():
    global last_image_path
    if last_image_path:
        with open(last_image_path, "rb") as img_file:
            encoded_string = base64.b64encode(img_file.read()).decode('utf-8')
            return jsonify({'image': encoded_string})
    else:
        return jsonify({'error': 'No image available.'}), 404

@app.route('/last_image_png', methods=['GET'])
def get_last_image_png():
    global last_image_path
    if last_image_path:
        # Lê o conteúdo do arquivo de imagem
        with open(last_image_path, 'rb') as img_file:
            img_bytes = img_file.read()
        # Retorna o conteúdo da imagem como resposta
        return send_file(io.BytesIO(img_bytes), mimetype='image/png')
    else:
        return jsonify({'error': 'No image available.'}), 404

@app.route('/last_n_image_png', methods=['GET'])
def get_last_N_image_png():
    global last_N_image_path
    if last_N_image_path:
        # Lê o conteúdo do arquivo de imagem
        with open(last_N_image_path, 'rb') as img_file:
            img_bytes = img_file.read()
        # Retorna o conteúdo da imagem como resposta
        return send_file(io.BytesIO(img_bytes), mimetype='image/png')
    else:
        return jsonify({'error': 'No image available.'}), 404

@app.route('/last_image_png_fix', methods=['GET'])
def get_last_N_image_png_fix():
    latest_image_path = get_last_file(DOWNLOAD_DIR)
    if latest_image_path:
        # Lê o conteúdo do arquivo de imagem
        with open(latest_image_path, 'rb') as img_file:
            img_bytes = img_file.read()
        # Retorna o conteúdo da imagem como resposta
        return send_file(io.BytesIO(img_bytes), mimetype='image/png')
    else:
        return jsonify({'error': 'No image available.'}), 404

@app.route('/last_n_image_png_fix', methods=['GET'])
def get_last_N_image_png_fix():
    latest_N_image_path = get_last_file(DOWNLOAD_N_DIR)
    if latest_N_image_path:
        # Lê o conteúdo do arquivo de imagem
        with open(latest_N_image_path, 'rb') as img_file:
            img_bytes = img_file.read()
        # Retorna o conteúdo da imagem como resposta
        return send_file(io.BytesIO(img_bytes), mimetype='image/png')
    else:
        return jsonify({'error': 'No image available.'}), 404

if __name__ == '__main__':
    app.run()
