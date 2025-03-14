import sys, os, folium
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QMainWindow, QPushButton, QLineEdit
from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings

m = folium.Map(location=[35.86948392517847, -78.60383523380236], zoom_start=16)
m.save("map.html")

class MapWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Targetting Map")
        self.setGeometry(100, 100, 800, 600)

        self.mapDisplay = QWebEngineView(self)

        settings = self.mapDisplay.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)

        file_path = os.path.abspath("map.html")  # Adjust filename as needed
        local_url = QUrl.fromLocalFile(file_path)
        self.mapDisplay.setUrl(local_url)
        print(f"Loading file: {file_path}")

        layout = QVBoxLayout()
        layout.addWidget(self.mapDisplay)
        
        mapWidget = QWidget()
        mapWidget.setLayout(layout)
        self.setCentralWidget(mapWidget)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    map = MapWindow()
    map.show()

    app.exec()