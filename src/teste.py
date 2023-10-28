import streamdeck
import requests
from PIL import Image

# Initialize Stream Deck
deck = streamdeck.StreamDeck()

# Fetch images and URLs
anime_info = [{"image_url": "https://example.com/image1.jpg", "website_url": "https://anime1.com"},
              {"image_url": "https://example.com/image2.jpg", "website_url": "https://anime2.com"},
              # ... add more anime info
              ]

# Load images onto Stream Deck
for idx, info in enumerate(anime_info):
    response = requests.get(info["image_url"])
    image = Image.open(io.BytesIO(response.content))
    deck.set_key_image(idx, streamdeck.ImageOps.to_native_format(deck, image))

# Configure buttons to open websites
def on_button_change(deck, key, state):
    if state:
        webbrowser.open(anime_info[key]["website_url"])

deck.set_key_callback(on_button_change)

# Run indefinitely
deck.run()
