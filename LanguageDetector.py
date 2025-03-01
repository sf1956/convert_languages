import re
from collections import Counter
from pynput import keyboard
import nltk
from nltk.corpus import words
import pyperclip
import time

# Download the words corpus if you haven't already
try:
    nltk.data.find('corpora/words')
except LookupError:
    nltk.download('words')

class LanguageDetector:
    def __init__(self):
        """Initializes the LanguageDetector with language models, patterns, word lists, and mappings."""
        # Language models (for character frequency - used for language detection)
        self.en_freq = self.load_language_model("en")
        self.en_total = sum(self.en_freq.values())

        # Word lists (for checking word validity - not used for language detection)
        self.english_words = set(words.words())

        # Mappings (for conversion)
        self.en_to_he_mapping = {
            'a': 'ש', 'b': 'נ', 'c': 'ב', 'd': 'ג', 'e': 'ק', 'f': 'כ', 'g': 'ע', 'h': 'י', 'i': 'ן',
            'j': 'ח', 'k': 'ל', 'l': 'ך', 'm': 'צ', 'n': 'מ', 'o': 'ם', 'p': 'פ', 'q': '/', 'r': 'ר',
            's': 'ד', 't': 'א', 'u': 'ו', 'v': 'ה', 'w': '\'', 'x': 'ס', 'y': 'ט', 'z': 'ז',
            ' ': ' ', ',': 'ת', '.': 'ץ',  # Preserve spaces
            '0': '0', '1': '1', '2': '2', '3': '3', '4': '4',
            '5': '5', '6': '6', '7': '7', '8': '8', '9': '9'
        }
        self.he_to_en_mapping = {v: k for k, v in self.en_to_he_mapping.items()}

        # Text buffer
        self.typed_text = ""
        # Assume keyboard starts in English
        self.keyboard_language = "en"
        self.controller = keyboard.Controller()

        # Keyboard listener
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()

        print("Language Detector initialized.")

    def load_language_model(self, language):
        """Load or create a simple language model based on character frequencies."""
        if language == "en":
            return Counter({
                'e': 12.02, 't': 9.10, 'a': 8.12, 'o': 7.68, 'i': 7.31, 'n': 6.95, 's': 6.28,
                'r': 6.02, 'h': 5.92, 'd': 4.32, 'l': 3.98, 'u': 2.88, 'c': 2.71, 'm': 2.61,
                'f': 2.30, 'p': 1.82, 'g': 1.61, 'w': 1.46, 'y': 1.42, 'b': 1.49, 'v': 0.92,
                'k': 0.69, 'x': 0.17, 'j': 0.16, 'q': 0.11, 'z': 0.07,
                ' ': 18.0
            })
        else:
          return Counter()

    def detect_language_statistical(self, text):
        """Detect language using character frequency statistics."""
        if not text:
            return "unknown", 0

        en_score = 0
        for char in text.lower():
            en_score += self.en_freq.get(char, 0) / self.en_total
        
        if en_score>0:
          return "en", en_score
        else:
          return "unknown", 0

    def is_valid_english_word(self, word):
        """Check if a word is in the English dictionary."""
        return word.lower() in self.english_words

    def convert_hebrew_to_english(self, hebrew_text):
        """Convert Hebrew text to English using the mapping."""
        return ''.join(self.he_to_en_mapping.get(char, char) for char in hebrew_text)

    def convert_english_to_hebrew(self, english_text):
        """Convert English text to Hebrew using the mapping."""
        return ''.join(self.en_to_he_mapping.get(char, char) for char in english_text.lower())

    def is_hebrew(self, text):
        """Check if any characters in the text are Hebrew."""
        return any('\u0590' <= c <= '\u05FF' for c in text)

    def switch_keyboard_language(self, language):
        """Simulates switching the keyboard language."""
        print(f"Switching to {language}")
        self.controller.press(keyboard.Key.ctrl)
        self.controller.press(keyboard.Key.space)
        self.controller.release(keyboard.Key.space)
        self.controller.release(keyboard.Key.ctrl)
        time.sleep(0.3)  # Increased delay for reliability
        self.keyboard_language = language

    def clear_text(self, text_length):
        """Clears the existing text in the active window."""
        # Copy an empty string to the clipboard and paste it to clear the text
        pyperclip.copy("")
        self.controller.press(keyboard.Key.cmd)
        self.controller.press('v')
        self.controller.release('v')
        self.controller.release(keyboard.Key.cmd)
        time.sleep(0.2)  # Ensure the paste operation completes

    def write_to_active_window(self, text_to_write):
      """Writes the given text to the active window, replacing the current word."""
      # Clear the existing text by simulating backspaces
      for _ in range(len(self.typed_text)):
        self.controller.press(keyboard.Key.backspace)
        self.controller.release(keyboard.Key.backspace)
        time.sleep(0.01)  # Small delay between backspaces

      # Paste the new text
      pyperclip.copy(text_to_write)
      self.controller.press(keyboard.Key.cmd)
      self.controller.press('v')
      self.controller.release('v')
      self.controller.release(keyboard.Key.cmd)
      time.sleep(0.1)

    def process_word(self):
        """Process the current word buffer based on the logic defined in the request."""
        if not self.typed_text:
            return

        # Determine the keyboard layout based on the typed text
        is_hebrew_text = self.is_hebrew(self.typed_text)
        keyboard_layout = "he" if is_hebrew_text else "en"

        # Determine the language based on keyboard layout and word validity
        if keyboard_layout == "en":
            if self.is_valid_english_word(self.typed_text):
                language = "en"
                print(f"KB=En, Lang=En, word={self.typed_text}")
            else:
                language = "he"
                hebrew_word = self.convert_english_to_hebrew(self.typed_text)
                print(f"KB=En, Lang=He, word={hebrew_word}")
                # Write back and switch keyboard
                self.write_to_active_window(hebrew_word)
                self.switch_keyboard_language("he")
        elif keyboard_layout == "he":
            english_candidate = self.convert_hebrew_to_english(self.typed_text)
            if self.is_valid_english_word(english_candidate):
                language = "en"
                print(f"KB=He, Lang=En, word={english_candidate}")
                self.write_to_active_window(english_candidate)
                self.switch_keyboard_language("en")

            else:
                language = "he"
                print(f"KB=He, Lang=He, word={self.typed_text}")
        else:
            language = "Unknown"
            print(f"KB=Unknown, Lang=Unknown, word={self.typed_text}")

        self.typed_text = ""

    def on_press(self, key):
        """Handle key press events."""
        try:
            if key == keyboard.Key.space:
                # Process the word when space is pressed
                self.process_word()

            elif key == keyboard.Key.backspace:
                if self.typed_text:
                    self.typed_text = self.typed_text[:-1]
            elif hasattr(key, 'char') and key.char is not None:
                self.typed_text += key.char
            elif key == keyboard.Key.shift_l or key == keyboard.Key.shift_r:
                # Toggle the keyboard status (this part remains)
                self.keyboard_language = "he" if self.keyboard_language == "en" else "en"
            elif key == keyboard.Key.esc:
                print("Exiting program...")
                self.stop()
                return False  # Stop the listener
        except Exception as e:
            print(f"Error handling key press: {e}")

    def stop(self):
        """Stop the listener and cleanup."""
        if self.listener:
            self.listener.stop()
        print("Language detector stopped.")


if __name__ == "__main__":
  try:
      detector = LanguageDetector()
      detector.listener.join()
  except KeyboardInterrupt:
        print("\nExiting...")
  finally:
      if 'detector' in locals():
          detector.stop()

