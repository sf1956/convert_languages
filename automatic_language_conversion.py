#!/usr/bin/env python3
import enchant
from pynput import keyboard
import time

class LanguageLayoutManager:
    def __init__(self):
        # Initialize variables
        self.current_word = ""
        self.current_layout = None
        self.enchant_dict_en = enchant.Dict("en_US")
        self.controller = keyboard.Controller()
        self.typing_programmatically = False  # Flag to ignore programmatic typing
        self.first_word_processed = False  # Flag to track if the first word has been processed

        # English to Hebrew character mapping (simplified example)
        self.en_to_he_mapping = {
            'a': 'ש', 'b': 'נ', 'c': 'ב', 'd': 'ג', 'e': 'ק', 'f': 'כ', 'g': 'ע', 'h': 'י', 'i': 'ן',
            'j': 'ח', 'k': 'ל', 'l': 'ך', 'm': 'צ', 'n': 'מ', 'o': 'ם', 'p': 'פ', 'q': '/', 'r': 'ר',
            's': 'ד', 't': 'א', 'u': 'ו', 'v': 'ה', 'w': '׳', 'x': 'ס', 'y': 'ט', 'z': 'ז',
            ' ': ' ', ',': 'ת', '.': 'ץ',  # Preserve spaces and punctuation
            '0': '0', '1': '1', '2': '2', '3': '3', '4': '4',
            '5': '5', '6': '6', '7': '7', '8': '8', '9': '9'
        }

        # Hebrew to English character mapping (reverse mapping)
        self.he_to_en_mapping = {v: k for k, v in self.en_to_he_mapping.items()}

    def on_press(self, key):
        """Handle key press events."""
        if self.typing_programmatically:
            return  # Ignore programmatically typed keys

        # Exit on Escape key
        if key == keyboard.Key.esc:
            return False  # Stop listener and exit program
        
        try:
            if key == keyboard.Key.space:
                if not self.first_word_processed:
                    if self.current_word:
                        self.process_word()
                    self.first_word_processed = True
                self.current_word = ""
            elif key == keyboard.Key.enter:
                self.first_word_processed = False
                self.current_word = ""
            elif hasattr(key, 'char') and key.char is not None:
                char = key.char.lower()
                self.current_word += char
                if not self.first_word_processed:
                    self.update_layout(char)
        except Exception as e:
            print(f"Error in on_press: {e}")

    def update_layout(self, char):
        """Determine the current keyboard layout based on the character."""
        if 'a' <= char <= 'z':
            self.current_layout = "En"
        elif '\u05D0' <= char <= '\u05EA':  # Hebrew Unicode range
            self.current_layout = "He"

    def process_word(self):
        """Process the typed word and apply the rules."""
        if not self.current_layout:
            return  # No layout determined yet

        # Detect language and apply rules
        if self.current_layout == "En":
            if self.enchant_dict_en.check(self.current_word):
                print(f"KB=En, Lang=En: '{self.current_word}' - No change")
                return  # Rule 1: Do nothing if English word on English layout
            else:
                print(f"KB=En, Lang=He: '{self.current_word}' - Converting to Hebrew")
                self.replace_and_switch("He")  # Rule 3: Convert to Hebrew
        elif self.current_layout == "He":
            converted_word = ''.join(self.he_to_en_mapping.get(c, c) for c in self.current_word)
            if self.enchant_dict_en.check(converted_word):
                print(f"KB=He, Lang=En: '{self.current_word}' - Converting to English")
                self.replace_and_switch("En")  # Rule 4: Convert to English
            else:
                print(f"KB=He, Lang=He: '{self.current_word}' - No change")
                return  # Rule 2: Do nothing if Hebrew word on Hebrew layout

    def replace_and_switch(self, target_layout):
        """Replace the typed word, add a space, and switch keyboard layout."""
        # Convert the word based on target layout
        if target_layout == "He":
            converted_word = ''.join(self.en_to_he_mapping.get(c, c) for c in self.current_word)
        else:
            converted_word = ''.join(self.he_to_en_mapping.get(c, c) for c in self.current_word)

        # Simulate backspaces to delete the typed word plus the space
        time.sleep(0.1)  # Small delay to ensure input is processed
        for _ in range(len(self.current_word) + 1):
            self.controller.press(keyboard.Key.backspace)
            self.controller.release(keyboard.Key.backspace)
            time.sleep(0.01)  # Small delay between key presses

        # Type the converted word followed by a space
        self.typing_programmatically = True
        self.controller.type(converted_word + ' ')
        self.typing_programmatically = False

        # Switch keyboard layout
        self.switch_layout(target_layout)

    def switch_layout(self, layout):
        """Switch the keyboard layout (macOS example)."""
        # Note: This uses Ctrl+Space; adjust based on your system's shortcut
        if layout == "En":
            self.controller.press(keyboard.Key.ctrl)
            self.controller.press(keyboard.Key.space)
            self.controller.release(keyboard.Key.space)
            self.controller.release(keyboard.Key.ctrl)
        elif layout == "He":
            self.controller.press(keyboard.Key.ctrl)
            self.controller.press(keyboard.Key.space)
            self.controller.release(keyboard.Key.space)
            self.controller.release(keyboard.Key.ctrl)
        print(f"Switched layout to {layout}")
        time.sleep(0.1)  # Allow time for layout switch

def main():
    """Start the keyboard listener."""
    manager = LanguageLayoutManager()
    with keyboard.Listener(on_press=manager.on_press) as listener:
        print("Starting keyboard listener. Type words and press space to process.")
        listener.join()

if __name__ == "__main__":
    main()

    