import enchant
from enchant.checker import SpellChecker
from enchant.tokenize import EmailFilter, URLFilter, WikiWordFilter
import re
import os
import sys

# Choose the appropriate module for reading single key presses
if os.name == 'nt':  # Windows
    import msvcrt
    def get_key():
        return msvcrt.getch().decode('utf-8', errors='ignore')
else:  # macOS and Linux
    import termios, tty
    def get_key():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

#enchant.set_param("enchant.myspell.dictionary.path", "/enchant_dicts")

def is_hebrew_word_tolerant(word, tolerance=1):
    """
    Check if the given word is a valid Hebrew word, allowing for small spelling errors.

    Args:
        word (str): The word to check.
        tolerance (int): The maximum number of spelling errors allowed (default: 1).

    Returns:
        bool: True if the word is likely a Hebrew word, False otherwise.
    """
    # Remove leading and trailing spaces
    word = word.strip()

    # Return False if the word is empty
    if not word:
        return False

    try:
        # Create a dictionary object for Hebrew
        d = enchant.Dict("he")

        # Check if the word exists in the Hebrew dictionary without changes
        if d.check(word):
            return True

        # Use SpellChecker to check for near-matches
        chkr = SpellChecker("he", filters=[EmailFilter, URLFilter, WikiWordFilter])
        
        # Use a regex filter to only keep hebrew letters
        only_hebrew_letters_word = re.sub(r"[^א-ת]", "", word)
        
        chkr.set_text(only_hebrew_letters_word)
        
        # Iterate through the errors in the word
        for err in chkr:
            # If the word is similar enough, count it as correct
            if len(err.word) > 3:
                suggestions = d.suggest(err.word)
                if err.word in suggestions:
                    print(f"The corrected word is: {suggestions[0]}")
                    return True
            if len(err.word) <= 3:
                suggestions = d.suggest(err.word)
                if len(err.word) == len(only_hebrew_letters_word) and err.word in suggestions :
                    print(f"The corrected word is: {suggestions[0]}")
                    return True
        
        return False

    except enchant.errors.DictNotFoundError:
        # Handle case where Hebrew dictionary is not installed
        print("Hebrew dictionary not found. Please install it (e.g., 'hunspell-he' on Ubuntu).")
        return False

# Example usage
if __name__ == "__main__":
    print("Press Esc to exit.")
    while True:
        # Get input from the user
        print("Enter a word: ", end="", flush=True)

        word = ""
        while True:
            key = get_key()
            if key == chr(27):  # Esc key
                print("\nExiting program.")
                exit()
            elif key == '\r' or key == '\n':
                print()
                break
            elif key == '\x7f' or key == '\b': # Backspace or Delete
                if len(word) > 0:
                    word = word[:-1]
                    print('\b \b', end='', flush=True)
            else:
              word += key
              print(key, end="", flush=True)

        
        # Check if the user pressed enter without typing anything
        if not word:
            continue

        # Check if it's a Hebrew word and print the result
        if is_hebrew_word_tolerant(word):
            print("True")
        else:
            print("False")
