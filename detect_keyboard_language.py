import subprocess

def get_keyboard_layout():
    """
    Detects the current keyboard layout on macOS.

    Returns:
        str: The name of the current keyboard layout (e.g., "U.S.", "Hebrew"),
             or "Unknown" if the layout cannot be determined.
    """
    try:
        # Use the 'defaults' command to read the current keyboard layout
        process = subprocess.run(
            ['defaults', 'read', 'AppleCurrentKeyboardLayoutInputSource'],
            capture_output=True,
            text=True,
            check=True  # Raise an exception for non-zero exit codes
        )
        output = process.stdout.strip()

        # Parse the output to extract the keyboard layout name
        if "KeyboardLayout Name" in output:
            start_index = output.find("KeyboardLayout Name =") + len("KeyboardLayout Name =")
            end_index = output.find(";", start_index)
            layout_name = output[start_index:end_index].strip()
            # Remove surrounding quotes if present
            if layout_name.startswith('"') and layout_name.endswith('"'):
                layout_name = layout_name[1:-1]
            return layout_name
        else:
            return "Unknown"

    except subprocess.CalledProcessError as e:
        print(f"Error reading keyboard layout: {e}")
        return "Unknown"
    except FileNotFoundError:
        print("Error: 'defaults' command not found (are you on macOS?)")
        return "Unknown"

if __name__ == "__main__":
    current_layout = get_keyboard_layout()
    if current_layout != "Unknown":
        print(f"Current keyboard layout: {current_layout}")

        # You can add language mappings for user-friendly output if needed
        language_map = {
            "U.S.": "English (U.S.)",
            "Hebrew": "Hebrew",
            # Add more mappings as needed based on common layouts
            # You can find layout names by switching layouts and running the script
        }
        friendly_name = language_map.get(current_layout, current_layout) # Default to layout name if not in map
        print(f"Friendly name: {friendly_name}")

        if current_layout == "Hebrew":
            print("Keyboard layout is set to Hebrew.")
        elif current_layout == "U.S.": # Or other common English layouts like British, etc.
            print("Keyboard layout is set to English (U.S.).")
        else:
            print(f"Keyboard layout is set to: {friendly_name}")
    else:
        print("Could not detect keyboard layout.")
        