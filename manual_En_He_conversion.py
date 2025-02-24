#!/Users/shmuelfarkash/Code/.ibkr_venv312/bin/python

from pynput import keyboard
import pyperclip
import time

# Initialize variables
typed_text = ""
ctrl_pressed = False

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

# Function to switch keyboard language
def switch_keyboard_language(language, controller):
    print(f"Switching to {language}")
    controller.press(keyboard.Key.ctrl)
    controller.press(keyboard.Key.space)
    controller.release(keyboard.Key.space)
    controller.release(keyboard.Key.ctrl)
    time.sleep(0.3)  # Increased delay for reliability

# Function to convert text and set language
def convert_text(text, controller):
    is_hebrew = any('\u0590' <= c <= '\u05FF' for c in text)
    if not is_hebrew:
        # English to Hebrew
        mapped_text = ''.join(en_to_he_mapping.get(char, char) for char in text)
        switch_keyboard_language("Hebrew", controller)
        return mapped_text
    else:
        # Hebrew to English
        mapped_text = ''.join(he_to_en_mapping.get(char, char) for char in text)
        switch_keyboard_language("English", controller)
        return mapped_text

# Function to clear existing text
def clear_text(controller, text_length):
    # Copy an empty string to the clipboard and paste it to clear the text
    pyperclip.copy("")
    controller.press(keyboard.Key.cmd)
    controller.press('v')
    controller.release('v')
    controller.release(keyboard.Key.cmd)
    time.sleep(0.2)  # Ensure the paste operation completes

# Key press handler
def on_press(key):
    global typed_text, ctrl_pressed
    try:
        # Handle Ctrl key press
        if key == keyboard.Key.ctrl:
            ctrl_pressed = True
            return

        # Handle Ctrl+L for conversion
        if ctrl_pressed and hasattr(key, 'char') and key.char == 'l':
            if typed_text:
                controller = keyboard.Controller()
                converted_text = convert_text(typed_text, controller)
                print(f"Typed text: {repr(typed_text)}")
                print(f"Converted text: {repr(converted_text)}")

                # Step 1: Move cursor to the start of the text
                for _ in range(len(typed_text)):
                    controller.press(keyboard.Key.left)
                    controller.release(keyboard.Key.left)
                time.sleep(0.1)

                # Step 2: Select all typed text
                controller.press(keyboard.Key.shift)
                for _ in range(len(typed_text)):
                    controller.press(keyboard.Key.right)
                    controller.release(keyboard.Key.right)
                controller.release(keyboard.Key.shift)
                time.sleep(0.1)

                # Step 3: Clear the selected text
                clear_text(controller, len(typed_text))

                # Step 4: Paste the converted text
                pyperclip.copy(converted_text)
                controller.press(keyboard.Key.cmd)
                controller.press('v')
                controller.release('v')
                controller.release(keyboard.Key.cmd)

                typed_text = ""  # Reset after conversion
            return

        # Handle normal typing
        if not ctrl_pressed:
            if hasattr(key, 'char') and key.char is not None:
                typed_text += key.char
            elif key == keyboard.Key.space:
                typed_text += ' '
            elif key == keyboard.Key.backspace and typed_text:
                typed_text = typed_text[:-1]
            elif key == keyboard.Key.enter:
                print(f"Enter pressed, resetting typed_text: {repr(typed_text)}")
                typed_text = ""

    except AttributeError:
        pass

# Key release handler
def on_release(key):
    global ctrl_pressed
    if key == keyboard.Key.ctrl:
        ctrl_pressed = False

# Start the listener
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
    