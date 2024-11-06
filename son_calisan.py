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

    _esm = """
    import maplibregl from 'https://cdn.jsdelivr.net/npm/maplibre-gl@4.7.1/+esm';
    import mapboxGlArcgisFeatureserver from 'https://cdn.jsdelivr.net/npm/mapbox-gl-arcgis-featureserver@0.0.8/+esm';

    export function render({ model, el }) {
      const map = new maplibregl.Map({
        container: el,
        style: model.tile_url,
        center: model.center,
        zoom: model.zoom,
        pitch: model.pitch,  // Adding pitch for 3D perspective
        bearing: model.bearing,  // Adding bearing to rotate map
        antialias: true
      });

      const controlsContainer = document.createElement('div');
      controlsContainer.style.position = 'absolute';
      controlsContainer.style.top = '10px';
      controlsContainer.style.left = '10px';
      controlsContainer.style.zIndex = '1';
      controlsContainer.style.backgroundColor = 'white';
      controlsContainer.style.padding = '2px';
      controlsContainer.style.borderRadius = '3px';
      //controlsContainer.style.width = '150px';
      //controlsContainer.style.height = '50px';

      const firstLayerButton = document.createElement('button');
      firstLayerButton.textContent = 'İlk Katman';
      firstLayerButton.onclick = () => {
        model.show_first_layer = !model.show_first_layer;
      };
      controlsContainer.appendChild(firstLayerButton);

      const secondLayerButton = document.createElement('button');
      secondLayerButton.textContent = 'İlçe Sınırları';
      secondLayerButton.onclick = () => {
        model.show_second_layer = !model.show_second_layer;
      };
      controlsContainer.appendChild(secondLayerButton);

      const arcgisLayerButton = document.createElement('button');
      arcgisLayerButton.textContent = 'ArcGIS Katmanı';
      arcgisLayerButton.onclick = () => {
        model.show_arcgis_layer = !model.show_arcgis_layer;
      };
      controlsContainer.appendChild(arcgisLayerButton);

      const styleDropdown = document.createElement('select');
      ['Basic', 'Positron', 'Dark Matter'].forEach(style => {
        const option = document.createElement('option');
        option.value = style;
        option.text = style;
        styleDropdown.add(option);
      });
      
      styleDropdown.onchange = (event) => {
        model.tile_url = event.target.value === 'Basic'
          ? "https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json"
          : event.target.value === 'Positron'
          ? "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
          : "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json";
      };
      controlsContainer.appendChild(styleDropdown);

      el.appendChild(controlsContainer);

      map.on('load', () => {
        const addLayers = () => {
            if (!map.getSource('geojson-layer')) {
                map.addSource('geojson-layer', {
                    type: 'geojson',
                    data: JSON.parse(model.geojson_data),
                });

                map.addLayer({
                    id: 'geojson-layer',
                    type: 'fill',
                    source: 'geojson-layer',
                    layout: {},
                    paint: {
                        'fill-color': '#0080ff',
                        'fill-opacity': 0.5
                    }
                });
            }

            if (!map.getSource('geojson-layer-2')) {
                map.addSource('geojson-layer-2', {
                    type: 'geojson',
                    data: JSON.parse(model.geojson_data_2),
                });

                map.addLayer({
                    id: 'geojson-layer-2',
                    type: 'fill',
                    source: 'geojson-layer-2',
                    layout: {},
                    paint: {
                        'fill-color': '#ff0000',
                        'fill-opacity': 0.5
                    }
                });
            }

            if (!map.getSource('featureserver-src')) {
                const fsSourceId = 'featureserver-src';
                const service = new mapboxGlArcgisFeatureserver(fsSourceId, map, {
                    url: `${model.arcgis_url}?token=${model.token}`
                });

                console.log(`${model.arcgis_url}?token=${model.token}`);
                console.log("aa");


                map.addLayer({
                    'id': 'fill-lyr',
                    'source': fsSourceId,
                    'type': 'fill',
                    'paint': {
                        'fill-opacity': 0.5,
                        'fill-color': '#B42222'
                    }
                });
            }

            if (!map.getSource('openmaptiles')) {
                map.addSource('openmaptiles', {
                  url: 'https://api.maptiler.com/tiles/v3/tiles.json?key=ka2CI0XYdBCZt32lmrGA',
                  type: 'vector',
                });

                map.addLayer(
                  {
                    'id': '3d-buildings',
                    'source': 'openmaptiles',
                    'source-layer': 'building',
                    'type': 'fill-extrusion',
                    'minzoom': 15,
                    'paint': {
                      'fill-extrusion-color': '#aaa',
                      'fill-extrusion-height': [
                        'interpolate',
                        ['linear'],
                        ['zoom'],
                        15,
                        0,
                        16,
                        ['get', 'render_height']
                      ],
                      'fill-extrusion-base': ['get', 'render_min_height'],
                      'fill-extrusion-opacity': 0.6
                    }
                  }
                );
            }

            // Katmanların görünürlüğünü ayarlayın
            map.setLayoutProperty('geojson-layer', 'visibility', model.show_first_layer ? 'visible' : 'none');
            map.setLayoutProperty('geojson-layer-2', 'visibility', model.show_second_layer ? 'visible' : 'none');
            map.setLayoutProperty('fill-lyr', 'visibility', model.show_arcgis_layer ? 'visible' : 'none');
        };

        // İlk katman eklenir
        addLayers();

        // Stil değişikliği yapıldığında katmanları yeniden ekleme
        model.on('change:tile_url', () => {
            map.setStyle(model.tile_url);
            map.on('styledata', () => {
                addLayers();
            });
        });

        window.addEventListener('resize', () => {
            map.resize();
        });

        model.on('change:center', () => {
            map.setCenter(model.center);
        });

        model.on('change:zoom', () => {
            map.setZoom(model.zoom);
        });

        // Katmanların görünürlüğünü izleme ve güncelleme
        model.on('change:show_first_layer', () => {
            map.setLayoutProperty('geojson-layer', 'visibility', model.show_first_layer ? 'visible' : 'none');
        });

        model.on('change:show_second_layer', () => {
            map.setLayoutProperty('geojson-layer-2', 'visibility', model.show_second_layer ? 'visible' : 'none');
        });

        model.on('change:show_arcgis_layer', () => {
            map.setLayoutProperty('fill-lyr', 'visibility', model.show_arcgis_layer ? 'visible' : 'none');
        });

    });
    }
    """

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