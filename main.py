import os
from flask import Flask, send_file, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

app = Flask(__name__)

# Define the directory path of app.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/download_image', methods=['GET'])
def download_image():
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
        driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)

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
            downloaded_image_filename = os.path.join(DOWNLOAD_DIR, sorted_image_files[0])

            # Close the browser
            driver.quit()

            # Return the downloaded image directly
            return send_file(downloaded_image_filename, mimetype='image/png', as_attachment=True)
        else:
            # Close the browser
            driver.quit()

            return jsonify({'error': 'No image files downloaded.'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run()
