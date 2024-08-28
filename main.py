import time
import pytesseract
from PIL import ImageGrab, Image, ImageDraw
import pygetwindow as gw
from pypresence import Presence
import pystray
from pystray import MenuItem as item
import threading
from PIL import Image
import json

def load_config():
    with open('config.json', 'r') as file:
        return json.load(file)

# Load configuration
config = load_config()
client_id = config.get('client_id', 'default_client_id')  # Use 'default_client_id' as fallback

# Configure Tesseract executable path if needed
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\simon\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

# Define the area to capture (left, top, right, bottom)
capture_area = (0, 1100, 500, 1250)  # Adjust the coordinates for your specific area

# List of street names to check
street_names = [
    "Hillview Road", "Sandstone Road", "Independence Parkway", "Main Street", "Park Street",
    "Orchard Boulevard", "Durham Road", "Freedom Avenue", "Liberty Way", "Industrial Road",
    "Georgia Avenue", "Cross Street", "Medical Way", "Grand Avenue", "Cline Street",
    "Southern Avenue", "Madison Court", "Fairfax Road", "Valley Drive", "Arbor Lane",
    "Franklin Court", "Academy Place", "Emerson Road", "Joyner Road", "Colonial Drive",
    "Vine Street", "Lee Street", "Gibson Lane", "Pineview Circle", "Spring Creek Road",
    "Northern Way", "Lakeview Court", "Iron Road", "Maple Street", "Cedar Street",
    "Grant Street", "Terrace Drive", "Oak Valley Drive", "Elm Street"
]

# Global flag to signal the main loop to stop
running = True

# Function to check if the game window is open
def is_game_open(game_title):
    windows = gw.getWindowsWithTitle(game_title)
    return len(windows) > 0

# Function to capture the screen area and extract text
def capture_and_extract_text(area):
    screen = ImageGrab.grab(bbox=area)
    text = pytesseract.image_to_string(screen)
    return text.strip()

# Function to update Discord Rich Presence
def update_discord_presence(street_name):
    RPC.update(
        details=f"Driving on {street_name}",
        large_image="driving",  # You can set this to a key for an image you've uploaded to your Discord app
        small_image="car",  # Same here, for a smaller image
        state="Enjoying the ride!"
    )

# Function to clear Discord Rich Presence
def clear_discord_presence():
    try:
        RPC.update(
            details="",       # Clear the details
            large_image="",   # Clear the large image
            small_image="",   # Clear the small image
            state="Idle"      # Set a neutral state
        )
    except Exception as e:
        print(f"Error clearing Discord presence: {e}")

# Initialize Discord Rich Presence
RPC = Presence(client_id)
RPC.connect()

def main_loop(game_title):
    global running
    while running:
        if is_game_open(game_title):
            text = capture_and_extract_text(capture_area)
            for street in street_names:
                if street in text:
                    update_discord_presence(street)  # Update Discord Rich Presence
                    break
        else:
            clear_discord_presence()  # Clear Discord Rich Presence when the game is closed
            break
        time.sleep(5)  # Check every 5 seconds

def on_quit(icon, item):
    global running
    running = False
    clear_discord_presence()  # Clear Discord Rich Presence before quitting
    icon.stop()

def create_image(icon_path):
    # Generate an image for the tray icon
    return Image.open(icon_path)

def setup_tray_icon():
    icon = pystray.Icon("test_icon", create_image("custom_icon.ico"), "ERLC Street Viewer")
    icon.menu = pystray.Menu(item('Quit', on_quit))
    icon.run_detached()

if __name__ == "__main__":
    game_title = "Roblox"  # Replace with your game's window title
    
    # Start the background task
    threading.Thread(target=main_loop, args=(game_title,), daemon=True).start()
    
    # Start the system tray icon
    setup_tray_icon()