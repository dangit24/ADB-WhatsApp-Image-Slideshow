# WhatsApp Image Slideshow

This project monitors a specified directory on an Android device for new WhatsApp images, pulls new images to a local directory, and displays them in a Tkinter slideshow application. The slideshow can run in full screen on any connected monitor and shuffle the images after displaying all new images.

## Features

- Monitors an Android device directory for new `.jpg` and `.jpeg` images.
- Pulls new images to a local directory.
- Displays images in a Tkinter slideshow.
- Fullscreen mode that can be toggled with `F11`.
- Esc key to exit fullscreen mode.
- Shuffles images after displaying all newly added images.

## Requirements

- Python 3.x
- Tkinter
- Pillow
- `screeninfo` library
- ADB (Android Debug Bridge)
- Android device with ADB enabled and WhatsApp Business installed

## Installation

1. **Install Python and required libraries:**

    ```bash
    pip install pillow screeninfo
    ```

2. **Install ADB:**

    Follow instructions from the [Android Developer website](https://developer.android.com/studio/command-line/adb) to install ADB on your system.

3. **Ensure your Android device has ADB enabled:**

    - Enable Developer Options on your device.
    - Enable USB Debugging in Developer Options.

## Usage

1. **Clone the repository:**

    ```bash
    git clone https://github.com/dangit24/ADB-WhatsApp-Image-Slideshow.git
    cd ADB-WhatsApp-Image-Slideshow
    ```

2. **Configure the directories:**

    Modify the `device_dir`, `directory_to_list`, and `local_directory` variables in the script as needed.

    ```python
    device_dir="/sdcard/whatsapp business/media/whatsapp business images"
    directory_to_list = "\"/sdcard/whatsapp business/media/whatsapp business images\""
    local_directory = ".\\whatsapp_images"  # Local directory to save the files
    ```

3. **Run the script:**

    ```bash
    python ADB_WhatsApp_Image_Slideshow.py
    ```

4. **Toggle fullscreen mode:**

    - Press `F11` to enter/exit fullscreen mode.
    - Press `Escape` to exit fullscreen mode.

## Code Overview

### `run_adb_command`

Runs an ADB command and returns the output.

### `list_files_on_device`

Lists files in a specified directory on the Android device.

### `pull_file_from_device`

Pulls a file from the Android device to the local machine.

### `monitor_directory`

Monitors a specified directory on the device and pulls new files to a local directory.

### `SlideshowApp` Class

Handles the slideshow functionality, including image loading, resizing, and displaying. It also manages fullscreen toggling and shuffling of images.

- `update_images_list`: Updates and shuffles the list of images.
- `resize_image`: Resizes images to fit the Tkinter window while maintaining aspect ratio.
- `display_next_image`: Displays the next image in the slideshow.
- `add_image_to_slideshow`: Adds new images to the slideshow queue.
- `set_fullscreen_on_current_screen`: Sets the window to fullscreen on the current screen.
- `toggle_fullscreen`: Toggles fullscreen mode.
- `get_current_screen`: Gets the screen where the window is currently displayed.
- `parse_geometry`: Parses the window geometry.

### Configuration

Sets the directories for monitoring and saving images, as well as the interval for checking new files.

### Main

Starts monitoring the directory and running the Tkinter slideshow application.

## Contributing

Feel free to submit issues, fork the repository, and send pull requests.

## License

This project is licensed under the MIT License.
