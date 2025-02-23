#!/Users/shmuelfarkash/Code/.ibkr_venv312/bin/python

from pynput import keyboard
import pyperclip
import time

# Configuration
CONVERSION_THRESHOLD = 5  # Number of letters before checking/conversion

# Initialize variables
typed_text = ""
current_layout = "English"  # Assume starting layout; can be set manually
is_processing = False  # Flag to lock state until Enter

# Mapping from English (QWERTY) to Hebrew characters
en_to_he_mapping = {
    'a': 'ש', 'b': 'נ', 'c': 'ב', 'd': 'ג', 'e': 'ק', 'f': 'כ', 'g': 'ע', 'h': 'י', 'i': 'ן',
    'j': 'ח', 'k': 'ל', 'l': 'ך', 'm': 'צ', 'n': 'מ', 'o': 'ם', 'p': 'פ', 'q': '/', 'r': 'ר',
    's': 'ד', 't': 'א', 'u': 'ו', 'v': 'ה', 'w': '\'', 'x': 'ס', 'y': 'ט', 'z': 'ז',
    ' ': ' ', ',': 'ת', '.': 'ץ',  # Preserve spaces
    '0': '0', '1': '1', '2': '2', '3': '3', '4': '4',
    '5': '5', '6': '6', '7': '7', '8': '8', '9': '9'
}

# Mapping from Hebrew to English (QWERTY)
he_to_en_mapping = {v: k for k, v in en_to_he_mapping.items()}

# Function to switch keyboard language using pynput
def switch_keyboard_language(target_layout, controller):
    global current_layout
    if current_layout != target_layout:
        print(f"Switching from {current_layout} to {target_layout}")  # Debug
        controller.press(keyboard.Key.ctrl)
        controller.press(keyboard.Key.space)
        controller.release(keyboard.Key.space)
        controller.release(keyboard.Key.ctrl)
        time.sleep(0.2)  # Delay to ensure the switch registers
        current_layout = target_layout

# Function to convert text
def convert_text(text, from_layout):
    if from_layout == "English":
        # Convert English to Hebrew
        return ''.join(en_to_he_mapping.get(char, char) for char in text)
    else:
        # Convert Hebrew to English
        return ''.join(he_to_en_mapping.get(char, char) for char in text)

# Function to analyze and process text
def process_text(text, controller):
    global typed_text, is_processing
    if is_processing or len(text) < CONVERSION_THRESHOLD or not text.strip():
        return

    # Lock processing state
    is_processing = True
    
    # Check if text contains Hebrew characters
    is_hebrew = any('\u0590' <= c <= '\u05FF' for c in text)
    
    if current_layout == "English" and is_hebrew:
        # English layout, Hebrew text: Convert to Hebrew and switch to Hebrew
        converted_text = convert_text(text, "Hebrew")
        print(f"Typed (Hebrew on English layout): {repr(text)} -> Converted: {repr(converted_text)}")
        
        # Backspace to erase original text
        for _ in range(len(text)):
            controller.press(keyboard.Key.backspace)
            controller.release(keyboard.Key.backspace)
        
        # Paste converted text
        pyperclip.copy(converted_text)
        controller.press(keyboard.Key.cmd)
        controller.press('v')
        controller.release('v')
        controller.release(keyboard.Key.cmd)
        
        switch_keyboard_language("Hebrew", controller)
        typed_text = ""
    
    elif current_layout == "Hebrew" and not is_hebrew and any(c.isalnum() for c in text):
        # Hebrew layout, English text: Convert to English and switch to English
        converted_text = convert_text(text, "English")
        print(f"Typed (English on Hebrew layout): {repr(text)} -> Converted: {repr(converted_text)}")
        
        # Backspace to erase original text
        for _ in range(len(text)):
            controller.press(keyboard.Key.backspace)
            controller.release(keyboard.Key.backspace)
        
        # Paste converted text
        pyperclip.copy(converted_text)
        controller.press(keyboard.Key.cmd)
        controller.press('v')
        controller.release('v')
        controller.release(keyboard.Key.cmd)
        
        switch_keyboard_language("English", controller)
        typed_text = ""

# Key press handler
def on_press(key):
    global typed_text, is_processing
    controller = keyboard.Controller()
    
    try:
        char = key.char
        if char is not None:
            typed_text += char
            if not is_processing:  # Only process if not already locked
                process_text(typed_text, controller)
    except AttributeError:
        if key == keyboard.Key.space:
            typed_text += ' '
            if not is_processing:
                process_text(typed_text, controller)
        elif key == keyboard.Key.backspace and typed_text:
            typed_text = typed_text[:-1]
        elif key == keyboard.Key.enter:
            if not is_processing:
                process_text(typed_text, controller)
            is_processing = False  # Reset state on Enter
            typed_text = ""
            print(f"Enter pressed, reset. Current layout: {current_layout}")
        elif key == keyboard.Key.esc:
            print(f"Escape pressed, resetting. Typed text: {repr(typed_text)}")
            typed_text = ""
            is_processing = False  # Allow manual reset

# Start the listener
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
