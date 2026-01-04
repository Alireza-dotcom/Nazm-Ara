from PySide6.QtGui import QFontDatabase

def loadFont(font_path: str):
    """
    Registers a custom font file with the application's font database.
    Returns the name of the first font family found in the file.
    """
    # Attempt to add the font to the global application database
    font_id = QFontDatabase.addApplicationFont(font_path)

    # QFontDatabase returns -1 if the font file is invalid or cannot be opened
    if font_id < 0:
        print(f"Failed to load font: {font_path}")

    # Retrieve the list of families (names) associated with the loaded font ID
    font_families = QFontDatabase.applicationFontFamilies(font_id)

    # Ensure the file actually contains font data
    if not font_families:
        print(f"No font families found in: {font_path}")

    # Return the primary font family name (e.g., "Nunito" or "Vazirmatn")
    return font_families[0]
