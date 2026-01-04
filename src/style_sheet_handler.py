import re
from PySide6.QtCore import (
    QObject,
    QIODevice,
    QFile,
    QTextStream,
)


class StyleSheetHandler(QObject):
    """Handles loading, parsing, and dynamically updating the application's stylesheet (QSS)."""
    def __init__(self, parent_window):
        super().__init__(parent_window)
        self.parent_window = parent_window


    def setResourceQssPath(self, resource_qss_path: str):
        """Sets the path to the QSS resource file and triggers the initial stylesheet load."""
        self.resource_qss_path = resource_qss_path
        self.original_qss = self.loadResourceQss()
        self.updateStylesheet()


    def loadResourceQss(self):
        """Reads the QSS file from the resource system or local path."""
        file = QFile(self.resource_qss_path)

        if file.open(QIODevice.ReadOnly | QIODevice.Text):
            stream = QTextStream(file)
            content = stream.readAll()
            file.close()
            return content
        print(f"Resource file at {self.resource_qss_path} doesn't exist.")
        return ""


    def getMergedStylesheet(self):
        """
        Parses the original QSS and applies dynamic modifications.
        Updates font sizes based on scale factor and injects Latin/Persian font families.
        """
        scale_factor = self.getScaleFactor()
        
        lines = self.original_qss.split('\n')
        
        merged_lines = []
        
        for line in lines:
            # Dynamically scale pixel-based font sizes
            if 'font-size:' in line:
                line = self.scaleFontSizeInLine(line, scale_factor)
            # elif 'font-family:' in line:
            #     line = f'font-family: "{self.parent_window.latin_font_family}", "{self.parent_window.persian_font_family}";'
            merged_lines.append(line)

        merged_qss = '\n'.join(merged_lines)
        return merged_qss


    def scaleFontSizeInLine(self, line, scale_factor):
        """Uses regex to find px values in font-size declarations and scales them."""

        match = re.search(r'font-size:\s*(\d+)px', line)
        if match:
            original_size = int(match.group(1))
            # Calculate new size based on window scale factor
            new_size = int(original_size * scale_factor)
            line = line.replace(f"{original_size}px", f"{new_size}px")

        return line


    def getScaleFactor(self):
        """Calculates a multiplier based on the current window dimensions relative to a base size."""
        window_size = min(self.parent_window.width(), self.parent_window.height())
        base_window_size = 900

        scale_factor = window_size / base_window_size
        # Clamps the scaling between 0.95 and 1.5 to prevent extreme text sizes
        scale_factor = max(1, min(scale_factor, 1.5))

        return scale_factor


    def updateStylesheet(self):
        """Generates the modified QSS and applies it to the parent window."""
        if hasattr(self, "original_qss"):
            merged_qss = self.getMergedStylesheet()
            self.parent_window.setStyleSheet(merged_qss)
        else:
            print("No QSS resource path set.")
