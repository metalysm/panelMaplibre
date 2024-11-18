from pathlib import Path
import param
import panel as pn

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


url = "https://akomcbs.ibb.istanbul/server/rest/services/Hosted/sensor/FeatureServer/0"
params = {
    'username': username,
    'password': password,
    "token": token,
    "where": "1=1",
    "outFields": "*",
    "f": "json"
}

response = requests.get(url, params=params)
data = response.json()

# Yanıtın "features" dizisinde olup olmadığını kontrol edin
if "features" in data and response.status_code == 200:
    features = data["features"]
    for feature in features:
        print(feature)
else:
    print("Beklenen formatta özellik verisi yok:", data)


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
    show_3d_layer = param.Boolean(default=False, doc="Show or hide the 3d layer.")

    _esm = Path("paneltrialdeneme.js")

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
    arcgis_url = url,
    zoom=10,
    pitch=45, 
    bearing=-17,
    sizing_mode='stretch_both',
    min_height=500
)

# description = pn.pane.Markdown(
#     "## İstanbul İlçe Haritası\n\nBu harita İstanbul ilçelerinin GeoJSON verisiyle hazırlanmıştır.",
#     sizing_mode="stretch_width"
# )

# toggle_button = pn.widgets.Toggle(name='İlk katman', button_type='primary')
# toggle_button_2 = pn.widgets.Toggle(name='İlçe Sınırları', button_type='primary')
# toggle_button_arcgis = pn.widgets.Toggle(name='ArcGIS Katmanı', button_type='primary')
# map_style_dropdown = pn.widgets.Select(name='Harita Stili', options=list(map_styles.keys()), value='Basic')


# def toggle_layer(event):
#     map_component.show_first_layer = event.new

# def toggle_layer_2(event):
#     map_component.show_second_layer = event.new

# def toggle_arcgis_layer(event):
#     map_component.show_arcgis_layer = event.new

# def update_map_style(event):
#     map_component.tile_url = map_styles[event.new]

# # butonlar
# toggle_button.param.watch(toggle_layer, 'value')
# toggle_button_2.param.watch(toggle_layer_2, 'value')
# toggle_button_arcgis.param.watch(toggle_arcgis_layer, 'value')
# map_style_dropdown.param.watch(update_map_style, 'value')

pn.Column(
    # description,
    pn.Row(
        map_component,
        sizing_mode='stretch_both'
    ),
    # toggle_button,
    # toggle_button_2,
    # toggle_button_arcgis,
    # map_style_dropdown,
    sizing_mode='stretch_both'
).servable()