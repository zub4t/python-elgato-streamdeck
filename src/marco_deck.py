#!/usr/bin/env python3

#         Python Stream Deck Library
#      Released under the MIT license
#
#   dean [at] fourwalledcubicle [dot] com
#         www.fourwalledcubicle.com
#

# Example script showing basic library usage - updating key images with new
# tiles generated at runtime, and responding to button state change events.

import os
import threading
import json
from PIL import Image, ImageDraw, ImageFont
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper
import sys
import importlib
import time

# Folder location of image assets used by this example.
ASSETS_PATH = os.path.join(os.path.dirname(__file__), "Assets")
PROFILE = json.load(open(os.path.join(ASSETS_PATH, "work_profile.json")))
PARENT_PAGE= None
sys.path.append(os.path.join(ASSETS_PATH,"commands")) 
# Generates a custom tile with run-time generated text and custom image via the
# PIL module.
def render_key_image(deck, icon_filename, font_filename, label_text):
    # Resize the source image asset to best-fit the dimensions of a single key,
    # leaving a margin at the bottom so that we can draw the key title
    # afterwards.
    icon = Image.open(icon_filename)
    image = PILHelper.create_scaled_image(deck, icon, margins=[0, 0, 20, 0])

    # Load a custom TrueType font and use it to overlay the key index, draw key
    # label onto the image a few pixels from the bottom of the key.
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_filename, 14)
    draw.text((image.width / 2, image.height - 5), text=label_text, font=font, anchor="ms", fill="white")

    return PILHelper.to_native_format(deck, image)


# Returns styling information for a key based on its position and state.
def get_key_style(deck, key, state):
    # Last button in the example application is the exit button.
    if f"key{key}" in PROFILE:
        key_t = PROFILE.get(f"key{key}")
        icon = eval(key_t.get('icon'))
        return {
        "name": key_t.get('name'),
        "icon": os.path.join(ASSETS_PATH,   f"icons\\{icon}" ),
        "font": os.path.join(ASSETS_PATH,   f"fonts\\{key_t.get('font')}"  ),
        "label": key_t.get('label')
        }
    else:
        return {
        "name": "Not Set",
        "icon": os.path.join(ASSETS_PATH, "icons\\none.png"),
        "font": os.path.join(ASSETS_PATH, "fonts\\Roboto-Regular.ttf"),
        "label": "Not Set"
        }
def import_and_instantiate_class(module_name, class_name):
    try:
        # Import the module based on the string name
        module = importlib.import_module(module_name)
    except ImportError:
        print(f"Module {module_name} not found.")
        return None

    try:
        # Get the class from the module
        cls = getattr(module, class_name)
    except AttributeError:
        print(f"Class {class_name} not found in module {module_name}.")
        return None

    # Instantiate the class
    instance = cls()
    return instance

def key_execute_command(command):
    import_and_instantiate_class(command,command).command()

# Creates a new key image based on the key index, style and current key state
# and updates the image on the StreamDeck.
def update_key_image(deck, key, state):
    # Determine what icon and label to use on the generated key.
    key_style = get_key_style(deck, key, state)

    # Generate the custom key with the requested image and label.
    image = render_key_image(deck, key_style["icon"], key_style["font"], key_style["label"])

    # Use a scoped-with on the deck to ensure we're the only thread using it
    # right now.
    with deck:
        # Update requested key with the generated image.
        deck.set_key_image(key, image)


# Prints key state change information, updates rhe key image and performs any
# associated actions when a key is pressed.
def key_change_callback(deck, key, state):
    global PROFILE  
    global PARENT_PAGE  

    # Print new key state
    print("Deck {} Key {} = {}".format(deck.id(), key, state), flush=True)
    if(state):
        if(f"key{key}" in PROFILE):
            key_t = PROFILE.get(f"key{key}")
            if ("submenu" in  key_t):
                PARENT_PAGE=PROFILE
                PROFILE=key_t.get("submenu")
            elif ("command" in  key_t):
                if("Back" == key_t.get('command')):
                    PROFILE = PARENT_PAGE
                else:
                    key_execute_command(key_t.get('command'))
        for i in range(0,15):
            update_key_image(deck, i, False)

if __name__ == "__main__":
    streamdecks = DeviceManager().enumerate()

    print("Found {} Stream Deck(s).\n".format(len(streamdecks)))

    for index, deck in enumerate(streamdecks):
        # This example only works with devices that have screens.
        if not deck.is_visual():
            continue

        deck.open()
        deck.reset()

        print("Opened '{}' device (serial number: '{}', fw: '{}')".format(
            deck.deck_type(), deck.get_serial_number(), deck.get_firmware_version()
        ))

        # Set initial screen brightness to 30%.
        deck.set_brightness(100)

        # Set initial key images.
        for key in range(deck.key_count()):
            update_key_image(deck, key, False)

        # Register callback function for when a key state changes.
        deck.set_key_callback(key_change_callback)

        # Wait until all application threads have terminated (for this example,
        # this is when all deck handles are closed).
        for t in threading.enumerate():
            try:
                t.join()
            except RuntimeError:
                pass
