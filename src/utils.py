from PySide6.QtGui import QFontDatabase

def loadFont(font_path):
    font_id = QFontDatabase.addApplicationFont(font_path)
    if font_id < 0:
        print(f"Failed to load font: {font_path}")

    font_families = QFontDatabase.applicationFontFamilies(font_id)
    if not font_families:
        print(f"No font families found in: {font_path}")

    return font_families[0]
