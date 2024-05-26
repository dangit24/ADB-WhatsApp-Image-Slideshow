import os
import subprocess
import time
import sys
import random
from PIL import Image, ImageTk, ImageOps
import tkinter as tk
from threading import Thread
from screeninfo import get_monitors

def run_adb_command(command):
    """Run an ADB command and return the output."""
    print(command)
    startupinfo = None
    if sys.platform == "win32":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE

    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, startupinfo=startupinfo)
    if result.returncode != 0:
        raise Exception(f"Command failed: {result.stderr}")
    return result.stdout

def list_files_on_device(directory):
    """List files in a directory on the Android device."""
    command = ["adb", "shell", "ls", directory]
    output = run_adb_command(command)
    return output.splitlines()

def pull_file_from_device(device_path, local_path):
    """Pull a file from the Android device to the local machine."""
    command = "adb " + "pull " + device_path + " " + local_path
    output = run_adb_command(command)

def monitor_directory(directory_to_list, local_directory, interval=60):
    """Monitor the specified directory on the device and pull new files if they don't already exist locally."""
    seen_files = set()

    while True:
        try:
            current_files = set(list_files_on_device(directory_to_list))
            new_files = current_files - seen_files

            for new_file in new_files:
                if new_file.lower().endswith(('.jpg', '.jpeg')):
                    local_file_path = os.path.join(local_directory, new_file)
                    if not os.path.exists(local_file_path):
                        device_file_path = "\""+device_dir + "/"+ new_file+"\""
                        pull_file_from_device(device_file_path, local_file_path)
                        print(f"New file detected and pulled: {new_file}")
                        # Update the slideshow with the new image
                        app.add_image_to_slideshow(local_file_path)
                    else:
                        print(f"File already exists locally: {new_file}")

            seen_files = current_files
        except Exception as e:
            print(f"Error: {e}")

        time.sleep(interval)

class SlideshowApp:
    def __init__(self, root, image_folder, interval=10000):
        self.root = root
        self.image_folder = image_folder
        self.interval = interval
        self.image_files = []
        self.image_index = 0
        self.image_queue = []
        self.photo=""
        self.fullscreen = False
        self.new_image_flag = False

        # Create a frame for the image
        self.image_frame = tk.Frame(root, bg='black')
        self.image_frame.pack(fill=tk.BOTH, expand=tk.YES)

        # Create a label for the image
        self.image_label = tk.Label(self.image_frame, bg='black', fg='#fff', text='Starting Slideshow', font=('Arial bold',60), compound=tk.BOTTOM)
        self.image_label.pack(fill=tk.BOTH, expand=tk.YES, side="left")

        self.update_images_list()
        self.root.after(1000, self.display_next_image)  # Start displaying after 1 second to ensure window is rendered

        # Bind the F11 key to toggle full screen
        self.root.bind('<F11>', self.toggle_fullscreen)

        # Bind the ESC key to exit fullscreen
        self.root.bind("<Escape>", self.toggle_fullscreen)

    def update_images_list(self):
        self.image_files = [os.path.join(self.image_folder, f) for f in os.listdir(self.image_folder)
                            if f.lower().endswith(('.jpg', '.jpeg'))]
        random.shuffle(self.image_files)

    def resize_image(self, image):
        """Resize the image to fit within the Tkinter window while maintaining aspect ratio."""
        image = ImageOps.exif_transpose(image)
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()

        if window_width == 1 and window_height == 1:
            # If the window size is not properly initialized, use a default size
            window_width, window_height = 800, 600

        image_ratio = image.width / image.height
        window_ratio = window_width / window_height

        if image.width > image.height:
            # Landscape image
            if window_ratio > image_ratio:
                # Window is wider than image, fit to height
                new_height = window_height
                new_width = int(new_height * image_ratio)
            else:
                # Window is taller than image, fit to width
                new_width = window_width
                new_height = int(new_width / image_ratio)
        else:
            # Portrait image
            if window_ratio > image_ratio:
                # Window is wider than image, fit to height
                new_height = window_height
                new_width = int(new_height * image_ratio)
            else:
                # Window is taller than image, fit to width
                new_width = window_width
                new_height = int(new_width / image_ratio)

        return image.resize((new_width, new_height), Image.ANTIALIAS)

    def display_next_image(self):
        if self.image_queue:
            image_path = self.image_queue.pop(0)
            print("Displaying next image in queue:", image_path, "Images remaining:", len(self.image_queue))
        else:
            if not self.image_files:
                self.update_images_list()
            if not self.image_files:
                print("No images found in the image_files list.")
                image_path = None
            else:
                while True:
                    if not self.image_files:
                        print("No images left in the image_files list.")
                        image_path = None
                        break  # Exit the loop if there are no images left

                    if self.image_index == 0:
                        print("Restarting slideshow. Shuffling image list.")
                        self.update_images_list()
                        
                    if self.image_files:
                        self.image_index = self.image_index % len(self.image_files)
                        image_path = self.image_files[self.image_index]
                        print("Queue empty. Displaying image #", self.image_index, image_path)

                        try:
                            image = Image.open(image_path)
                            break  # Successfully loaded the image, exit the loop
                        except (FileNotFoundError, OSError) as e:
                            print(f"Error loading image {image_path}: {e}. Removing from list.")
                            del self.image_files[self.image_index]

                if self.image_files:
                    self.image_index = (self.image_index + 1) % len(self.image_files)
        try:
            if image_path:
                image = Image.open(image_path)
                resized_image = self.resize_image(image)
                self.photo = ImageTk.PhotoImage(resized_image)
                
        except (FileNotFoundError, OSError) as e:
            print(f"Error loading image {image_path}: {e}.")
            image_path = None

        dots = '.' * len(self.image_queue)
        self.image_label.config(image=self.photo, text=dots, font=('Arial bold', 60))
        self.image_label.image = self.photo
        
        # Determine the interval
        next_interval = self.interval if image_path else min(1000, self.interval)  # Reduce to 1 second if no images

        self.root.after(next_interval, self.display_next_image)

    def add_image_to_slideshow(self, *image_paths):
        self.image_queue.extend(image_paths)

        if not self.image_queue:
            # If the queue was empty, shuffle the list of images
            print("Shuffling image list")
            random.shuffle(self.image_files)
        
        dots = '.' * len(self.image_queue)
        self.image_label.config(image=self.photo, text=dots, font=('Arial bold',60))
        self.image_label.image = self.photo

    def set_fullscreen_on_current_screen(self):
        # Get the current screen's geometry
        current_screen = self.get_current_screen()
        print("Current screen:", current_screen)
        screen_width = current_screen.width
        screen_height = current_screen.height
        print("Geometry:", f"{screen_width}x{screen_height}+{current_screen.x}+{current_screen.y}")
        self.root.overrideredirect(True)
        # Set the window size to match the screen size
        self.root.geometry(f"{screen_width}x{screen_height}")
        self.root.wm_attributes("-topmost", True)
        # Move the window to this monitor and make it fullscreen
        self.root.geometry(f"+{current_screen.x}+{current_screen.y}")

    def get_current_screen(self):
        # Get the screen on which the window is currently displayed
        window_geometry = self.root.geometry()
        window_x, window_y, _, _ = self.parse_geometry(window_geometry)

        for monitor in get_monitors():
            if (monitor.x <= window_x < monitor.x + monitor.width and
                    monitor.y <= window_y < monitor.y + monitor.height):
                return monitor

    def parse_geometry(self, geometry):
        # Parse the window geometry string: "WxH+X+Y"
        geo_parts = geometry.split('+')
        size_parts = geo_parts[0].split('x')
        width = int(size_parts[0])
        height = int(size_parts[1])
        x = int(geo_parts[1])
        y = int(geo_parts[2])
        return x, y, width, height

    def toggle_fullscreen(self, event=None):
        if self.fullscreen:
            self.root.attributes('-fullscreen', False)
            self.root.wm_attributes("-topmost", False)
            self.root.overrideredirect(False)
            self.root.geometry("800x600")
            self.fullscreen = False
        else:
            # Get the screen on which the window is currently displayed
            self.set_fullscreen_on_current_screen()
            self.fullscreen = True
        return "break"

# Configuration
device_dir = "/sdcard/whatsapp business/media/whatsapp business images"
directory_to_list = "\"/sdcard/whatsapp business/media/whatsapp business images\""
local_directory = ".\\whatsapp_images"  # Local directory to save the files
interval = 2  # Check interval in seconds
slideshow_interval_seconds = 30

# Ensure the local directory exists
if not os.path.exists(local_directory):
    os.makedirs(local_directory)

# Start monitoring in a separate thread
monitor_thread = Thread(target=monitor_directory, args=(directory_to_list, local_directory, interval))
monitor_thread.daemon = True
monitor_thread.start()

# Start the slideshow
root = tk.Tk()
root.geometry("800x600")  # Set the initial window size
app = SlideshowApp(root, local_directory, slideshow_interval_seconds*1000)
root.mainloop()
