import time
import random
import threading
import ctypes
from pynput import keyboard

# Global flag to control the wiggler
is_running = False
wiggler_thread = None

def move_mouse_relative(dx, dy):
    """Move mouse using Windows API for better game compatibility."""
    # MOUSEEVENTF_MOVE = 0x0001
    ctypes.windll.user32.mouse_event(1, dx, dy, 0, 0)

def smooth_move(target_x, target_y):
    """Move mouse smoothly to target offset using small steps."""
    global is_running

    # Number of steps for smooth movement
    steps = random.randint(10, 20)

    # Calculate step sizes
    step_x = target_x / steps
    step_y = target_y / steps

    # Move in small increments
    for i in range(steps):
        if not is_running:
            break
        move_mouse_relative(int(step_x), int(step_y))
        # Small delay between steps for natural movement
        time.sleep(random.uniform(0.01, 0.03))

def random_mouse_wiggler():
    """Randomly moves the mouse to prevent AFK detection."""
    global is_running

    while is_running:
        # Generate random movement offsets (-50 to 50 pixels)
        offset_x = random.randint(-50, 50)
        offset_y = random.randint(-50, 50)

        # Move mouse smoothly using gradual steps
        smooth_move(offset_x, offset_y)

        # Random interval between movements (3 to 10 seconds)
        # Check more frequently to allow stopping
        wait_time = random.uniform(3, 10)
        start_time = time.time()
        while (time.time() - start_time) < wait_time and is_running:
            time.sleep(0.1)

def on_activate():
    """Toggle the mouse wiggler on/off."""
    global is_running, wiggler_thread
    is_running = not is_running

    if is_running:
        print("Mouse wiggler started!")
        wiggler_thread = threading.Thread(target=random_mouse_wiggler, daemon=True)
        wiggler_thread.start()
    else:
        print("Mouse wiggler stopped!")

if __name__ == "__main__":
    print("Press Alt+Shift+W to start/stop the mouse wiggler")

    # Set up hotkey listener
    with keyboard.GlobalHotKeys({
        '<alt>+<shift>+w': on_activate
    }) as listener:
        listener.join()