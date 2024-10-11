import param
import json
import panel as pn
from panel.reactive import ReactiveHTML

class MapLibreLayerMap(ReactiveHTML):
    attribution = param.String(doc="Map source attribution.")
    center = param.XYCoordinates(default=(28.06, 41.77), doc="The center of the map.")
    tile_url = param.String(doc="Tile source URL")
    zoom = param.Integer(default=13, bounds=(0, 21), doc="The map's zoom level")
    geojson_data = param.Dict(default={}, doc="GeoJSON data to plot as a layer.")

    _template = """
    <div id="map" style="width: 100%; height: 100%;"></div>
    """

    _scripts = {
        'render': """
            state.map = new maplibregl.Map({
                container: map,
                style: data.tile_url,
                center: data.center,
                zoom: data.zoom,
                pitch: 45,
                bearing: -17.6,  
                antialias: true  
            });
        """,

        'after_layout': """
            state.map.on('load', () => {
                // Add the vector tile source for 3D buildings
                state.map.addSource('openmaptiles', {
                    url: 'https://api.maptiler.com/tiles/v3/tiles.json?key=ka2CI0XYdBCZt32lmrGA',
                    type: 'vector'
                });

                // Find the label layer to insert the 3D layer below it
                const layers = state.map.getStyle().layers;
                let labelLayerId;
                for (let i = 0; i < layers.length; i++) {
                    if (layers[i].type === 'symbol' && layers[i].layout['text-field']) {
                        labelLayerId = layers[i].id;
                        break;
                    }
                }

                // Add 3D buildings layer
                state.map.addLayer({
                    'id': '3d-buildings',
                    'source': 'openmaptiles',
                    'source-layer': 'building',
                    'type': 'fill-extrusion',
                    'minzoom': 10,
                    'paint': {
                        'fill-extrusion-color': [
                            'interpolate',
                            ['linear'],
                            ['get', 'render_height'],
                            0, 'lightgray',
                            200, 'royalblue',
                            400, 'lightblue'
                        ],
                        'fill-extrusion-height': [
                            'interpolate',
                            ['linear'],
                            ['zoom'],
                            5, 0,
                            8, ['get', 'render_height']
                        ],
                        'fill-extrusion-base': ['case',
                            ['>=', ['get', 'zoom'], 16],
                            ['get', 'render_min_height'], 0
                        ]
                    },
                }, labelLayerId);

                // Add GeoJSON source and layer
                state.map.addSource('geojson-source', {
                    'type': 'geojson',
                    'data': data.geojson_data
                });

                // Add the GeoJSON layer (e.g., a fill layer)
                state.map.addLayer({
                    'id': 'geojson-layer',
                    'type': 'fill',
                    'source': 'geojson-source',
                    'paint': {
                        'fill-color': '#FF0000', 
                        'fill-opacity': 0.6  
                    }
                });
                // Add a pop-up on click
                state.map.on('click', 'geojson-layer', (e) => {
                    const coordinates = e.lngLat;
                    const properties = e.features[0].properties; // GeoJSON features properties

                    new maplibregl.Popup()
                        .setLngLat(coordinates)
                        .setHTML(`
                            <h4>Koordinat</h4>
                            <p>${coordinates}</p>
                        `)
                        .addTo(state.map);
                });
                state.map.resize(); 

                // Change the cursor to a pointer when hovering over the layer
                map.on('mouseenter', 'geojson-layer', () => {
                    map.getCanvas().style.cursor = 'pointer';
                });

                map.on('mouseleave', 'geojson-layer', () => {
                    map.getCanvas().style.cursor = '';
                });
            
            });
        """,

        'geojson_data': """
            if (state.map.getSource('geojson-source')) {
                state.map.getSource('geojson-source').setData(data.geojson_data);
            }
        """
    }

    _extension_name = 'maplibre'

    __css__ = ['https://unpkg.com/maplibre-gl@^4.7.1/dist/maplibre-gl.css']
    __javascript__ = ['https://unpkg.com/maplibre-gl@^4.7.1/dist/maplibre-gl.js']

pn.extension('maplibre', template='fast')

# Load your GeoJSON file
with open('k.geojson') as f:
    geojson_layer = json.load(f)

# Create the MapLibre layer map
layermap = MapLibreLayerMap(
    attribution='',
    geojson_data=geojson_layer,
    tile_url='https://api.maptiler.com/maps/basic-v2/style.json?key=ka2CI0XYdBCZt32lmrGA',
    zoom=int(8),
    center=(28.8, 41.1), 
    sizing_mode='stretch_both'
)

# Display the map
pn.Column(
    pn.Row(
        layermap.servable(),
        sizing_mode='stretch_both'
    )
)
