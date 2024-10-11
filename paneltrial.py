import param
import json
import panel as pn

from panel.reactive import ReactiveHTML

class MapLibreLayerMap(ReactiveHTML):

    attribution = param.String(doc="Map source attribution.")

    center = param.XYCoordinates(default=(28, 41), doc="The center of the map.")

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
                zoom: data.zoom
            });
        """,
        
        
        'after_layout': """


            state.map.on('load', () => {
                // Add GeoJSON layer
                if (Object.keys(data.geojson_data).length > 0) {
                    state.map.addSource('geojson-source', {
                        'type': 'geojson',
                        'data': data.geojson_data
                    });

                    state.map.addLayer({
                        'id': 'geojson-layer',
                        'type': 'line',
                        'source': 'geojson-source',
                        'paint': {
                            'line-color': '#ff0000',
                            'line-width': 2
                        }
                    });
                }
                state.map.resize(); 
            });
            
        """,
        
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
    tile_url='https://demotiles.maplibre.org/style.json',
    zoom=int(5),
    center=(28, 41),
    sizing_mode='stretch_both'
)

# Display the map

pn.Column(
    pn.Row(
        # layermap.controls(['min_alpha']).servable(target='sidebar'),
        layermap.servable(),
        sizing_mode='stretch_both'
    ),
)
