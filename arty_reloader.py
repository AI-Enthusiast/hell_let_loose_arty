import time
import random
import threading
import ctypes
from pynput import keyboard

# Global state
is_running = False
spam_thread = None

def send_key(key_code):
    """press using Windows API"""
    ctypes.windll.user32.keybd_event(key_code, 0, 0, 0)  # Key down
    time.sleep(0.01)
    ctypes.windll.user32.keybd_event(key_code, 0, 2, 0)  # Key up

def spam_r():
    """Continuously spam 'r' key"""
    global is_runningr
    r_key_code = 0x52  # Virtual key code for 'R'

    while is_running:
        send_key(r_key_code)
        time.sleep(random.uniform(0.2, 0.3  ))

def toggle_spam():
    """Toggle the spam on/off"""
    global is_running, spam_thread

    is_running = not is_running

    if is_running:
        print("Spam started! (Press Alt+Shift+R to stop)")
        spam_thread = threading.Thread(target=spam_r, daemon=True)
        spam_thread.start()
    else:
        print("Spam stopped! (Press Alt+Shift+R to start)")

def on_activate():
    """Callback when Alt+Shift+R is pressed"""
    toggle_spam()

# Set up the hotkey listener
with keyboard.GlobalHotKeys({
    '<alt>+<shift>+r': on_activate
}) as listener:
    print("Press Alt+Shift+R to toggle spam on/off")
    print("Press Ctrl+C to exit")
    listener.join()


