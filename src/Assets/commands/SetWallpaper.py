import requests
import os
import time
from PIL import Image
import ctypes
import sys
sys.path.append("..") 

from CommandInterface import CommandInterface  

class SetWallpaper(CommandInterface):
    FILE_PATH = os.path.join(os.path.dirname(__file__),"downloaded_image.png")
    def command(self):
        SetWallpaper.main()
    @staticmethod
    def fetch_image():
        url = "https://api.nekosapi.com/v2/images/random?filter[height.gt]=720&filter[width.gte]=1080"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'
        }
        response = requests.get(url, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            image_url = data['data']['attributes']['file']
            return image_url
        else:
            print(f"Failed to fetch image: {response.status_code}")
            return None

    # Function to save an image
    @staticmethod
    def save_image(image_url, file_extension):
        file_name = f"downloaded_image.{file_extension}"
        response = requests.get(image_url)

        if response.status_code == 200:
            with open(file_name, 'wb') as file:
                file.write(response.content)
            print(f"Image saved as {file_name}")
        else:
            print("Failed to download the image")

    # Function to convert an image to PNG
    @staticmethod
    def convert_and_save_image(image_url, original_extension):
        temp_file_name = f"temp_image.{original_extension}"

        response = requests.get(image_url)

        if response.status_code == 200:
            with open(temp_file_name, 'wb') as file:
                file.write(response.content)

            image = Image.open(temp_file_name)
            image.save(SetWallpaper.FILE_PATH, format="PNG")

            os.remove(temp_file_name)
            print(f"Image converted and saved as {SetWallpaper.FILE_PATH}")
        else:
            print("Failed to download the image")
    @staticmethod
    def set_wallpaper(image_path):
        # Check if the file exists
        if not os.path.exists(image_path):
            print(f"Image file does not exist: {image_path}")
            return False

        # SPI_SETDESKWALLPAPER is the system parameter info action to set the desktop wallpaper
        SPI_SETDESKWALLPAPER = 20

        # Use SystemParametersInfoA for ASCII characters and SystemParametersInfoW for wide characters (unicode)
        # Here, we use SystemParametersInfoW to support file paths with unicode characters
        result = ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, image_path, 3)

        if result:
            print(f"Wallpaper set successfully: {image_path}")
            return True
        else:
            print("Failed to set wallpaper")
            return False
    # Main function
    @staticmethod
    def main():
        # Fetch image URL
        image_url = SetWallpaper.fetch_image()
        if image_url:
            file_extension = image_url.split('.')[-1].lower()

            # Check file extension and save or convert accordingly
            if file_extension in ["png", "jpg", "jpeg"]:
                SetWallpaper.save_image(image_url, file_extension)
            elif file_extension == "webp":
                SetWallpaper.convert_and_save_image(image_url, file_extension)
            else:
                print("Unsupported file format")

            SetWallpaper.set_wallpaper(SetWallpaper.FILE_PATH)
