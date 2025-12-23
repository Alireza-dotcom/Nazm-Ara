from PySide6.QtCore import (
    QObject,
    QIODevice,
    QFile,
    QTextStream,
)


class StyleSheetHandler(QObject):
    def __init__(self, parent_window):
        super().__init__(parent_window)
        self.parent_window = parent_window


    def setResourceQssPath(self, resource_qss_path):
        self.resource_qss_path = resource_qss_path
        self.original_qss = self.loadResourceQss()


    def loadResourceQss(self):
        file = QFile(self.resource_qss_path)

        if file.open(QIODevice.ReadOnly | QIODevice.Text):
            stream = QTextStream(file)
            content = stream.readAll()
            file.close()
            return content
        print("Resource file doesn't exist")
        return ""


    def getMergedStylesheet(self):
        scale_factor = self.getScaleFactor()
        
        lines = self.original_qss.split('\n')
        
        merged_lines = []
        
        for line in lines:
            if 'font-size:' in line:
                line = self.scaleFontSizeInLine(line, scale_factor)
            elif 'font-family:' in line:
                line = f'font-family: "{self.parent_window.latin_font_family}", "{self.parent_window.persian_font_family}";'
            merged_lines.append(line)

        merged_qss = '\n'.join(merged_lines)
        return merged_qss


    def scaleFontSizeInLine(self, line, scale_factor):
        import re

        match = re.search(r'font-size:\s*(\d+)px', line)
        if match:
            original_size = int(match.group(1))
            new_size = int(original_size * scale_factor)
            line = line.replace(f"{original_size}px", f"{new_size}px")

        return line


    def getScaleFactor(self):
        window_size = min(self.parent_window.width(), self.parent_window.height())
        base_window_size = 900

        scale_factor = window_size / base_window_size
        scale_factor = max(0.9, min(scale_factor, 1.5))

        return scale_factor


    def updateStylesheet(self):
        merged_qss = self.getMergedStylesheet()
        self.parent_window.setStyleSheet(merged_qss)
