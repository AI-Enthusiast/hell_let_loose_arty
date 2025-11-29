import time
import requests
import random
import threading
import ctypes
from tqdm import tqdm
import win32gui
import pytesseract
from PIL import ImageGrab, Image
import cv2
import numpy as np
from pynput import keyboard
from pynput.keyboard import Key
from pynput.keyboard import Controller as KeyboardController
from pynput.mouse import Button
from pynput.mouse import Controller as MouseController
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from pyvirtualdisplay import Display
from selenium import webdriver
import random
import threading
import ctypes
from pynput import keyboard

suffix = 'https://www.hell-let-loose-calculator.com/'
maps = ['carentan', 'driel', 'el-alamein', 'foy', 'hill-400',
        'hürtgen-forest', 'kharkov', 'elsenborn-ridge', 'utah',
        'omaha', 'purple-heart-lane', 'remagen', 'stalingrad']

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Global state
is_running = False
spam_thread = None
operation_active = True
kill_switch_listener = None


def send_key(key_code):
    """Send a key press using Windows API"""
    ctypes.windll.user32.keybd_event(key_code, 0, 0, 0)  # Key down
    time.sleep(0.01)
    ctypes.windll.user32.keybd_event(key_code, 0, 2, 0)  # Key up


def spam_r():
    """Continuously spam 'r' key"""
    global is_running
    r_key_code = 0x52  # Virtual key code for 'R'

    for i in range(20):
        send_key(r_key_code)
        time.sleep(.2)


def on_f_key_press(key):
    """Handle key press events for kill switch"""
    global operation_active
    try:
        if hasattr(key, 'char') and key.char == 'f':
            print("\n[KILL SWITCH] F key pressed - stopping operation...")
            operation_active = False
            return False  # Stop listener
    except AttributeError:
        pass


def start_kill_switch_listener():
    """Start the keyboard listener for kill switch"""
    global kill_switch_listener, operation_active
    operation_active = True
    kill_switch_listener = keyboard.Listener(on_press=on_f_key_press)
    kill_switch_listener.start()
    print("[KILL SWITCH ACTIVE] Press 'f' key to stop current operation")


def stop_kill_switch_listener():
    """Stop the keyboard listener"""
    global kill_switch_listener
    if kill_switch_listener:
        kill_switch_listener.stop()
        kill_switch_listener = None


def reset_operation_flag():
    """Reset the operation flag to active"""
    global operation_active
    operation_active = True


def user_select_map():
    print("Available maps:")
    for i, map_name in enumerate(maps):
        print(f"{i + 1}. {map_name}")
    # choice = int(input("Select a map by number: ")) - 1
    # return maps[choice]


def fetch_map_data():
    # Get user input
    user_input = input("\nEnter map number or map name: ").strip()

    # Try to parse as number first
    try:
        map_index = int(user_input) - 1
        if 0 <= map_index < len(maps):
            selected_map = maps[map_index]
        else:
            print(f"Invalid number. Please enter a number between 1 and {len(maps)}")
            selected_map = None
    except ValueError:
        # If not a number, try to match the name
        user_input_lower = user_input.lower()
        if user_input_lower in maps:
            selected_map = user_input_lower
        else:
            print(f"Map '{user_input}' not found. Please check the spelling.")
            selected_map = None
    map_url = None
    if selected_map:
        print(f"\nSelected map: {selected_map}")
        map_url = suffix + selected_map
        print(f"URL: {map_url}")

    return map_url, selected_map


def select_gun(map_url, selected_map):
    url = None

    firefox_options = Options()

    # create the webdriver
    driver = webdriver.Firefox(options=firefox_options)

    # Move browser to second monitor (adjust x coordinate based on your monitor resolution)
    # If your primary monitor is 1920px wide, set x=1920 to move to second monitor
    driver.set_window_position(1920, 0)  # x=1920 (second monitor), y=0 (top)
    driver.maximize_window()  # Optional: maximize on second monitor

    try:
        print("Loading page...")
        driver.get(map_url)

        # Wait for the gun list elements to load (wait up to 15 seconds)
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "v-list-item-title")))

        # Find all gun names - they're in div elements with class "v-list-item-title text-h6"
        gun_elements = driver.find_elements(By.CSS_SELECTOR, "div.v-list-item-title.text-h6")
        gun_names = [gun.text.strip() for gun in gun_elements if gun.text.strip()]

        if gun_names:
            print(f"\nAvailable guns on {selected_map}:")
            for i, gun_name in enumerate(gun_names, 1):
                print(f"{i}. {gun_name}")

            # Get user input for gun selection
            gun_input = input("\nEnter gun number or gun name: ").strip()

            # Try to parse as number first
            try:
                gun_index = int(gun_input) - 1
                if 0 <= gun_index < len(gun_names):
                    selected_gun = gun_names[gun_index]
                else:
                    print(f"Invalid number. Please enter a number between 1 and {len(gun_names)}")
                    selected_gun = None
            except ValueError:
                # If not a number, try to match the name (case-insensitive)
                matched_gun = None
                for gun in gun_names:
                    if gun.lower() == gun_input.lower():
                        matched_gun = gun
                        break

                if matched_gun:
                    selected_gun = matched_gun
                else:
                    print(f"Gun '{gun_input}' not found. Please check the spelling.")
                    selected_gun = None

            if selected_map and selected_gun:
                print(f"\nYou have selected the map '{selected_map}' and the gun '{selected_gun}'.")
                url = f"{suffix}{selected_map}/{selected_gun}/"
            else:
                print("\nSelection incomplete. Please ensure both map and gun are selected.")
            return driver, url
        else:
            print("No guns found on this map page.")
            selected_gun = None
    except Exception as e:
        print(f"An error occurred while fetching gun data: {e}")
        selected_gun = None
    finally:
        return driver, url


# check if the v-card-section exists and extract data
def extract_gun_data(driver, url):
    artillery_data = None
    if url and driver:
        try:
            # Wait for the v-card-section to load
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                       "v-card-section.d-flex.flex-wrap")))

            # Find the v-card-section element
            card_section = driver.find_element(By.CSS_SELECTOR, "v-card-section.d-flex.flex-wrap")

            if card_section:
                # Extract all span elements that contain the values
                value_elements = card_section.find_elements(By.CSS_SELECTOR, "span")

                # Initialize variables to store extracted data
                mil_value = None
                distance_m = None
                degrees_bearing = None
                distance_d2 = None

                # Parse the values from the spans
                for span in value_elements:
                    text = span.text.strip()
                    if "MIL" in text:
                        mil_value = int(text.replace("MIL", "").strip())
                    elif "M" in text and "MIL" not in text:
                        distance_m = int(text.replace("M", "").strip())
                    elif "D" in text:
                        if degrees_bearing is None:
                            degrees_bearing = int(round(float(text.replace("D", "").strip())))
                        else:
                            distance_d2 = int(text.replace("D", "").strip())

                # Store the data in a dictionary for later use
                artillery_data = {
                    'elevation': mil_value,
                    'distance': distance_m,
                    'degrees': degrees_bearing,
                    'bearing_2': distance_d2
                }
            else:
                print("\nNo v-card-section found on the page.")

        except Exception as e:
            print(f"\nError extracting data: {e}")
    else:
        print("\nNo URL or driver available. Please run the previous cells first.")
    return artillery_data


def capture_screen_region(x, y, width, height):
    """Capture a specific region of the screen"""
    bbox = (x, y, x + width, y + height)
    screenshot = ImageGrab.grab(bbox)
    screenshot = screenshot.resize((screenshot.width * 3, screenshot.height * 3), Image.LANCZOS)

    return screenshot


def preprocess_image_for_ocr(image):
    """Preprocess image to improve OCR accuracy"""
    # Convert PIL image to OpenCV format
    img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # Convert to grayscale
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

    # Apply threshold to get black text on white background
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    # Optional: Apply some noise reduction
    # denoised = cv2.fastNlMeansDenoising(thresh)
    denoised = cv2.medianBlur(thresh, 3)

    return Image.fromarray(denoised)


def read_elevation_from_screen(x, y, width, height):
    """Read elevation value from specific screen coordinates"""
    # Capture the region
    screenshot = capture_screen_region(x, y, width, height)

    # Preprocess for better OCR
    processed = preprocess_image_for_ocr(screenshot)

    # Configure Tesseract to only recognize digits
    custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789MIL'

    # Extract text
    text = pytesseract.image_to_string(processed, config=custom_config)
    print(f"OCR Result: '{text.strip()}'")
    # Parse the elevation value
    try:
        elevation = int(''.join(filter(str.isdigit, text)))
        return elevation
    except ValueError:
        return None


def get_game_elevation():
    # Adjust coordinates based on where elevation appears on your screen
    x, y, width, height = 2399, 1260, 100, 30

    elevation = read_elevation_from_screen(x, y, width, height)
    if elevation is not None:
        return elevation
    else:
        return None


def get_game_degree():
    x, y, width, height = 1267, 1375, 26, 21
    degree = read_elevation_from_screen(x, y, width, height)
    if degree is not None:
        return degree
    else:
        return None


def rotate_pitch(target_pitch, gun_position, tolerance=0, max_iterations=50):
    """
    Rotate pitch to target value using feedback from get_game_elevation()

    Args:
        target_pitch: Target elevation in MIL
        gun_position: Current gun position (1 or 2)
        tolerance: Acceptable error in MIL (default 2)
        max_iterations: Maximum adjustment attempts (default 10)

    Returns:
        gun_position: Updated gun position
    """
    if gun_position != 1:
        gun_position = swap_gun_position(gun_position)

    keyboard_controller = KeyboardController()
    current_pitch = get_game_elevation()
    while current_pitch != target_pitch and max_iterations > 0:
        max_iterations -= 1
        current_pitch = get_game_elevation()
        try:
            pitch_difference = target_pitch - current_pitch
        except TypeError:
            print("Error reading current pitch. Retrying...")
            time.sleep(5)
            continue

        if abs(pitch_difference) <= tolerance:
            print(f"Pitch adjusted successfully: {current_pitch} MIL (target: {target_pitch} MIL)")
            break

        # Adjust pitch based on difference
        if pitch_difference > 0:
            print(f"Adjusting pitch up: current={current_pitch}, target={target_pitch}, diff={pitch_difference}")
            keyboard_controller.press('w')
            time.sleep(min(abs(pitch_difference) * 0.3, 2.0))  # Cap at 2 seconds
            keyboard_controller.release('w')
        elif pitch_difference < 0:
            print(f"Adjusting pitch down: current={current_pitch}, target={target_pitch}, diff={pitch_difference}")
            keyboard_controller.press('s')
            time.sleep(min(abs(pitch_difference) * 0.3, 2.0))  # Cap at 2 seconds
            keyboard_controller.release('s')

        time.sleep(0.3)  # Brief pause for game to update

    return gun_position


def rotate_degrees(target_degree, gun_position, tolerance=0, max_iterations=30):
    """
    Rotate to target degree using feedback from get_game_degree()

    Note: When in gun_position 2, the displayed degree is 48 less than the true value.
    For example, if get_game_degree() returns 52 in position 2, the true degree is 100.

    Args:
        target_degree: Target degree (true value)
        gun_position: Current gun position (1 or 2)
        tolerance: Acceptable error in degrees (default 2)
        max_iterations: Maximum adjustment attempts (default 10)

    Returns:
        gun_position: Updated gun position (unchanged)
    """
    keyboard_controller = KeyboardController()

    current_degree_raw = get_game_degree()
    while current_degree_raw != target_degree and max_iterations > 0:
        max_iterations -= 1
        current_degree_raw = get_game_degree()

        try:
            degree_difference = target_degree - current_degree_raw
        except TypeError:
            print("Error reading current degree. Retrying...")
            time.sleep(5)
            continue

        if abs(degree_difference) > 10:  # if the difference is large, swap position to see if it helps
            gun_position = swap_gun_position(gun_position)
            current_degree_raw = get_game_degree()

        # Adjust for gun_position offset
        # When in position 2, the displayed degree is 47 less than true value
        if gun_position == 2 and current_degree_raw is not None:
            current_degree = current_degree_raw + 47
        else:
            current_degree = current_degree_raw

        try:
            degree_difference = target_degree - current_degree
        except TypeError:
            print("Error reading adjusted current degree. Retrying...")
            time.sleep(5)
            continue

        # Normalize to -180 to 180 range for shortest rotation
        if degree_difference > 180:
            degree_difference -= 360
        elif degree_difference < -180:
            degree_difference += 360

        if abs(degree_difference) <= tolerance:
            print(f"Degree adjusted successfully: {current_degree}° (target: {target_degree}°)")
            break

        # Adjust degree based on difference
        if degree_difference > 0:
            print(
                f"Rotating right: current={current_degree}° (raw={current_degree_raw}°), target={target_degree}°, diff={degree_difference}°")
            keyboard_controller.press('d')
            time.sleep(min(abs(degree_difference) * 0.2, 3.0))  # Cap at 3 seconds
            keyboard_controller.release('d')
        elif degree_difference < 0:
            print(
                f"Rotating left: current={current_degree}° (raw={current_degree_raw}°), target={target_degree}°, diff={degree_difference}°")
            keyboard_controller.press('a')
            time.sleep(min(abs(degree_difference) * 0.1, 3.0))  # Cap at 3 seconds
            keyboard_controller.release('a')

        time.sleep(0.3)  # Brief pause for game to update

    return gun_position


def swap_gun_position(last_pos=1):
    # if in position 1 hold F2 for 1 second to go to position 2, else hold F1
    keyboard_controller = KeyboardController()
    if last_pos == 1:
        keyboard_controller.press(Key.f2)
        time.sleep(1.2)
        keyboard_controller.release(Key.f2)
        return 2
    else:
        keyboard_controller.press(Key.f1)
        time.sleep(1.2)
        keyboard_controller.release(Key.f1)
        return 1


def swap_windwow(count=1):
    # press alt+tab count times holding alt
    keyboard_controller = KeyboardController()
    keyboard_controller.press(Key.alt)
    for i in range(count):
        keyboard_controller.press(Key.tab)
        keyboard_controller.release(Key.tab)
        time.sleep(0.25)
    keyboard_controller.release(Key.alt)


def get_active_window_title():
    # Get the currently active window handle
    hwnd = win32gui.GetForegroundWindow()
    window_title = win32gui.GetWindowText(hwnd)
    print(f"Active window: {window_title}")
    return window_title


def swap_to_window(window_name="Hell Let Loose  "):
    current_window, count = get_active_window_title(), 1
    while current_window != window_name:
        swap_windwow(count)
        time.sleep(1)
        current_window = get_active_window_title()
        count += 1


def reload_gun(gun_position):
    keyboard_controller = KeyboardController()
    if gun_position != 2:
        gun_position = swap_gun_position(gun_position)

    # reload the gun by pressing 'r'
    spam_r()

    return gun_position


def fire_gun(gun_position):
    if gun_position != 1:
        gun_position = swap_gun_position(gun_position)

    # fire the gun by pressing the left mouse button
    mouse_controller = MouseController()
    time.sleep(.2)  # hold for 0.1 seconds
    mouse_controller.press(Button.left)
    mouse_controller.release(Button.left)

    return gun_position


def fire_x_times(x, gun_position):
    global operation_active
    for i in tqdm(range(x), desc="Firing artillery rounds"):
        if not operation_active:
            print("\n[KILL SWITCH] Firing operation cancelled")
            break
        gun_position = reload_gun(gun_position)

        gun_position = fire_gun(gun_position)

    return gun_position


def saturate_area(driver,
                  base_url: str,
                  center_x: float,
                  center_y: float,
                  radius: float = 50.0,
                  step_size: float = 10.0,
                  shots_per_location: int = 2,
                  gun_position: int = 1,
                  randomize_order: bool = True) -> int:
    """
    Saturate an area by firing at multiple points within a radius.

    Args:
        driver: Selenium webdriver instance
        base_url: Base URL without coordinates (e.g., ".../Allies%20South%20Western%20Gun/")
        center_x: Center X coordinate
        center_y: Center Y coordinate
        radius: Radius in map units to saturate (default 50.0)
        step_size: Distance between firing points (default 10.0)
        shots_per_location: Number of shots per location (default 2)
        gun_position: Current gun position (1 or 2)
        randomize_order: Randomize firing order to avoid patterns (default True)

    Returns:
        gun_position: Updated gun position after operation
    """
    global operation_active
    import math

    # Generate grid of points within radius
    points = []
    x_offset = -radius
    while x_offset <= radius:
        y_offset = -radius
        while y_offset <= radius:
            # Check if point is within circular radius
            distance = math.sqrt(x_offset ** 2 + y_offset ** 2)
            if distance <= radius:
                target_x = center_x + x_offset
                target_y = center_y + y_offset
                points.append((target_x, target_y))
            y_offset += step_size
        x_offset += step_size

    print(f"\nSaturating area: {len(points)} target locations")

    # Randomize order if requested
    if randomize_order:
        random.shuffle(points)

    # Visit each point and fire
    for idx, (target_x, target_y) in enumerate(points, 1):
        if not operation_active:
            print("\n[KILL SWITCH] Area saturation cancelled")
            break

        # Construct URL with target coordinates
        target_url = f"{base_url}{target_x}/{target_y}"

        print(f"\n[{idx}/{len(points)}] Targeting: ({target_x:.2f}, {target_y:.2f})")

        # Navigate to target location
        driver.get(target_url)
        time.sleep(1)  # Wait for page update

        # Extract gun data for this location
        gun_data = extract_gun_data(driver, target_url)
        swap_to_window()
        if gun_data:
            # Adjust aim to target
            gun_position = rotate_degrees(gun_data['degrees'], gun_position)
            gun_position = rotate_pitch(gun_data['elevation'], gun_position)

            # Fire shots at this location
            gun_position = fire_x_times(shots_per_location, gun_position)
        else:
            print(f"Warning: Could not extract gun data for location ({target_x}, {target_y})")

    print("\nArea saturation complete!")
    return gun_position


def main():
    global operation_active

    user_select_map()
    map_url, selected_map = fetch_map_data()
    if map_url and selected_map:
        swap_to_window("hell_let_loose_arty – arty_website.py")
        driver, url = select_gun(map_url, selected_map)
        swap_to_window("hell_let_loose_arty – arty_website.py")
        starting_degrees = get_game_degree()
        if url:

            driver.get(url)

            time.sleep(5)  # wait for page to load

            # every .1 check for the gun data
            gun_data = None
            old_gun_data = None
            old_gun_pitch = get_game_elevation()  # idk if this is always the same to FIXME
            gun_position = 1  # start in position 1
            swap_to_window("Hell Let Loose Calculator — Mozilla Firefox")
            while True:
                gun_data = extract_gun_data(driver, url)

                if gun_data != old_gun_data:
                    print("\nUpdated artillery data:")
                    for key, value in gun_data.items():
                        print(f"  {key}: {value}")
                    options = input(
                        "\nNew artillery data detected. Press 'f' to fire, 's' to saturate area, or Enter to skip: ").strip().lower()
                    if options == 'f':
                        amount = int(input("Enter number of rounds to fire (default 2): ").strip())

                        # Start kill switch listener before operation
                        start_kill_switch_listener()
                        swap_to_window()

                        # Rotate to target degree and pitch using feedback loops
                        gun_position = rotate_degrees(gun_data['degrees'], gun_position)
                        gun_position = rotate_pitch(gun_data['elevation'], gun_position)

                        gun_position = fire_x_times(amount, gun_position)

                        # Stop kill switch listener after operation
                        stop_kill_switch_listener()
                        reset_operation_flag()

                        old_gun_data = gun_data
                    elif options == 's':
                        current_url = driver.current_url
                        base_url = current_url.rsplit('/', 2)[0] + '/'  # everything up to gun name
                        print(f"Base URL for saturation: {base_url}")
                        # Example: https://.../purple-heart-lane/Allies%20South%20Western%20Gun/584.96/600.09
                        center_x = float(current_url.split('/')[-2])
                        center_y = float(current_url.split('/')[-1])

                        # Start kill switch listener before operation
                        start_kill_switch_listener()

                        gun_position = saturate_area(
                            driver=driver,
                            base_url=base_url,
                            center_x=center_x,
                            center_y=center_y,
                            radius=20.0,  # 50 map units radius
                            step_size=5.0,  # Fire every 15 map units
                            shots_per_location=1,
                            gun_position=gun_position
                        )

                        # Stop kill switch listener after operation
                        stop_kill_switch_listener()
                        reset_operation_flag()
                time.sleep(0.1)
        else:
            print("No valid gun URL constructed.")


if __name__ == "__main__":
    main()
