#!/Users/shmuelfarkash/Code/.ibkr_venv312/bin/python

from pynput import keyboard
import pyperclip
import time

# Initialize variable to store typed text
typed_text = ""

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
def switch_keyboard_language(language, controller):
    # Simulate Control+Space to cycle input sources
    # Assumes two input sources: English and Hebrew
    print(f"Switching to {language}")  # Debug
    controller.press(keyboard.Key.ctrl)
    controller.press(keyboard.Key.space)
    controller.release(keyboard.Key.space)
    controller.release(keyboard.Key.ctrl)
    time.sleep(0.2)  # Delay to ensure the switch registers

# Function to convert text and set language
def convert_text(text, controller):
    is_hebrew = any('\u0590' <= c <= '\u05FF' for c in text)
    if not is_hebrew:
        # English to Hebrew: Convert without reversing
        mapped_text = ''.join(en_to_he_mapping.get(char, '') for char in text)
        switch_keyboard_language("Hebrew", controller)
        return mapped_text
    else:
        # Hebrew to English: Convert without reversing
        mapped_text = ''.join(he_to_en_mapping.get(char, '') for char in text)
        switch_keyboard_language("English", controller)
        return mapped_text

# Key press handler
def on_press(key):
    global typed_text
    try:
        char = key.char
        if char is not None:
            typed_text += char
    except AttributeError:
        if key == keyboard.Key.space:  # Explicitly handle spacebar
            typed_text += ' '
        elif key == keyboard.Key.backspace and typed_text:
            typed_text = typed_text[:-1]
        elif key == keyboard.Key.enter:  # Reset on Enter
            print(f"Enter pressed, resetting typed_text. Previous value: {repr(typed_text)}")  # Debug
            typed_text = ""  # Reset to start over
        elif key == keyboard.Key.esc:
            if typed_text:
                controller = keyboard.Controller()
                converted_text = convert_text(typed_text, controller)
                print(f"Typed text: {repr(typed_text)}")  # Debug
                print(f"Converted text: {repr(converted_text)}")  # Debug

                for _ in range(len(typed_text)):
                    controller.press(keyboard.Key.backspace)
                    controller.release(keyboard.Key.backspace)
                
                pyperclip.copy(converted_text)
                controller.press(keyboard.Key.cmd)
                controller.press('v')
                controller.release('v')
                controller.release(keyboard.Key.cmd)

                typed_text = ""

# Start the listener
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
    