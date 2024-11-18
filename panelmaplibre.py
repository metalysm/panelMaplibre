import param
import panel as pn
from pathlib import Path

from panel.custom import JSComponent
import requests

token_url = "https://akomcbs.ibb.istanbul/geoportal/sharing/rest/generateToken"
username = "akomays"
password = "LV!ak1Qc"

# Set token request parameters
params = {
    'username': username,
    'password': password,
    'client': 'referer',  # Or 'referer' , 'requestip'
    'referer': 'https://akomcbs.ibb.istanbul/server/rest/services/Hosted/sensor/FeatureServer/0',
    'f': 'json'
}

response = requests.post(token_url, data=params)
if response.status_code == 200 and "token" in response.json():
    token = response.json()["token"]
    print("Generated Token:", token)
else:
    print("Error generating token:", response.json())


url = "https://akomcbs.ibb.istanbul/server/rest/services/Hosted/sensor/FeatureServer/0/query"
params = {
    'username': username,
    'password': password,
    "token": token,
    "where": "1=1",
    "outFields": "*",
    "f": "json"
}

# Use the token to fetch data
response = requests.get(url, params=params)

# Check if response is JSON or HTML
try:
    data = response.json()
    if "features" in data:
        features = data["features"]
        for feature in features:
            print(feature)
    else:
        print("Expected data format is not found in response:", data)
except ValueError:
    # If JSON parsing fails, print the text to see the HTML response
    print("Response is not JSON. Response text:", response.text)


url2 = "https://akomcbs.ibb.istanbul/server/rest/services/Hosted/depremler/FeatureServer/0/query"
params = {
    'username': username,
    'password': password,
    "token": token,
    "where": "1=1",
    "outFields": "*",
    "f": "json",
}

# Use the token to fetch data
response2 = requests.get(url2, params=params)

# Check if response is JSON or HTML
try:
    data = response2.json()
    if "features" not in data:
        print("Expected data format is not found in response2:", data)
        
except ValueError:
    # If JSON parsing fails, print the text to see the HTML response
    print("Response2 is not JSON. Response2 text:", response2.text)


class MapLibreComponent(JSComponent):
    # attribution = param.String(doc="Tile source attribution.")
    center = param.XYCoordinates(default=(28.9784, 41.0082), doc="The center of the map.")
    zoom = param.Integer(default=10, bounds=(0, 21), doc="The map's zoom level.")
    pitch = param.Integer(default=45, bounds=(0, 60), doc="The map's pitch (tilt) for 3D view.")
    bearing = param.Integer(default=-17, bounds=(-180, 180), doc="The map's rotation.")
    geojson_data = param.String()
    geojson_data_2 = param.String()
    token = param.String(doc="Token for ArcGIS layer.")
    tile_url = param.String(doc="Tile source URL with {x}, {y}, {z}.")
    arcgis_url = param.String(doc="arcgis url")
    show_first_layer = param.Boolean(default=False, doc="Show or hide the first layer.")
    show_second_layer = param.Boolean(default=False, doc="Show or hide the second layer.")
    show_arcgis_layer = param.Boolean(default=False, doc="Show or hide the ArcGIS layer.")
    show_arcgis_layer2 = param.Boolean(default=False, doc="Show or hide the ArcGIS layer 2.")
    show_3d_layer = param.Boolean(default=False, doc="Show or hide the 3d layer.")

    _esm = Path("map_scripts.js")


    _stylesheets = ['https://unpkg.com/maplibre-gl@^4.7.1/dist/maplibre-gl.css']

pn.extension(template='fast')

with open('k.geojson', 'r', encoding='utf-8') as f:
    geojson_data = f.read()

with open('ilce.geojson', 'r', encoding='utf-8') as f:
    geojson_data_2 = f.read()

map_styles = {
    'Basic': "https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json",
    'Positron': "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
    'Dark Matter': "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"
}

map_component = MapLibreComponent(
    # attribution='Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    geojson_data=geojson_data,
    geojson_data_2=geojson_data_2,
    tile_url= map_styles['Basic'],
    center=(28.9784, 41.0082),
    # center=(151.1, -33.5),
    token=token,
    arcgis_url = url,
    zoom=10,
    pitch=45, 
    bearing=-17,
    sizing_mode='stretch_both',
    min_height=500,
)

pn.Column(
    pn.Row(
        map_component,
        sizing_mode='stretch_both'
    ),
    sizing_mode='stretch_both'
).servable()