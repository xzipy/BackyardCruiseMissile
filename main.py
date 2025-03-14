import sys, os, folium, json, random
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QMainWindow, QPushButton, QLineEdit
from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
from shapely.geometry import Polygon
from router import create_route

with open("mapMarkers.json", "r") as file:
    jsonData = json.load(file)

def clearMap():
    mInit = folium.Map(location=[35.86948392517847, -78.60383523380236], zoom_start=16)

    for i in jsonData["noZones"]:
        polygon_coords = jsonData["noZones"][i]
        folium.Polygon(
            locations=polygon_coords,
            color='red',
            fill=True,
            fill_color='red'
        ).add_to(mInit)

    folium.Marker(
        location=[35.87343576932817, -78.60694073708956],
        popup='Home',
        icon=folium.Icon(color='green', icon='home')
    ).add_to(mInit)

    global m
    m = mInit
    m.save("map.html")

def planRoute(end_coord):
    print(f'Pressed w/ {end_coord}')
    try:
        lat, lon = end_coord.split(',')
        route = None
        route = create_route((lat, lon))
        print(route)
        if route is None:
            print('No path found')
        else:
            print(f'Path found: Length {len(route)}')
            folium.PolyLine(route, color='orange', weight=2.5, opacity=1).add_to(m)
            for i in range(1, len(route)-1):
                print(route[i])
                folium.CircleMarker(
                    location=route[i],
                    radius=2,
                    color='orange',
                    fill=True,
                    fillColor='orange',
                ).add_to(m)
            m.save("map.html")
            print("Map updated with route and saved to map.html")
            map.reloadMap(m)
            print("Reloaded")

    except ValueError:
        print("Invalid coordinate format")

def setCoord():
    end_coord = map.coordInput.text().split(',')
    map.setDestMarker(end_coord)

def randCoord():
    end_coord = [random.uniform(35.86512049627014, 35.872364972140814), random.uniform(-78.6081064355563, -78.60102032682744)]
    map.changeInputText(f'{end_coord[0]},{end_coord[1]}')
    map.setDestMarker(end_coord)

class MapWindow(QMainWindow):

    def setDestMarker(self, coords):
        clearMap()

        folium.Marker(
            location=coords,
            popup='Destination',
            icon=folium.Icon(color='red', icon='screenshot')
        ).add_to(m)

        map.reloadMap(m)

    def changeInputText(self, text):
        self.coordInput.setText(text)

    def reloadMap(self, m):
        m.save("map.html")
        file_path = os.path.abspath("map.html")
        local_url = QUrl.fromLocalFile(file_path)
        self.mapDisplay.setUrl(local_url)

    def __init__(self):
        clearMap()
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

        buttonLayout = QHBoxLayout()

        self.coordInput = QLineEdit(self)
        self.coordInput.setPlaceholderText("Enter a coordinate")
        self.submitButton = QPushButton("Submit")
        self.submitButton.clicked.connect(lambda: planRoute(self.coordInput.text()))
        self.randDest = QPushButton('Random')
        self.randDest.clicked.connect(lambda: randCoord())
        self.setDest = QPushButton('Set')
        self.setDest.clicked.connect(lambda: setCoord())

        buttonLayout.addWidget(self.submitButton)
        buttonLayout.addWidget(self.coordInput)
        buttonLayout.addWidget(self.setDest)
        buttonLayout.addWidget(self.randDest)

        layout = QVBoxLayout()
        layout.addWidget(self.mapDisplay)
        layout.addLayout(buttonLayout)
        
        mapWidget = QWidget()
        mapWidget.setLayout(layout)
        self.setCentralWidget(mapWidget)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    map = MapWindow()
    map.show()

    app.exec()