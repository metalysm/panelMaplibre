function renderMap(mapElement, tileUrl, center, zoom) {
    const map = new maplibregl.Map({
        container: mapElement,
        style: tileUrl,
        center: center,
        zoom: zoom
    });
    return map;
}

function afterLayout(map, geojsonData) {
    map.on('load', () => {
        if (Object.keys(geojsonData).length > 0) {
            map.addSource('geojson-source', {
                'type': 'geojson',
                'data': geojsonData
            });

            map.addLayer({
                'id': 'geojson-layer',
                'type': 'line',
                'source': 'geojson-source',
                'paint': {
                    'line-color': '#ff0000',
                    'line-width': 2
                }
            });
        }

        // Add a pop-up on click
        map.on('click', 'geojson-layer', (e) => {
            const coordinates = e.lngLat;
            const properties = e.features[0].properties;
            const description = JSON.stringify(properties, null, 2);

            // Create a popup and set its content
            new maplibregl.Popup()
                .setLngLat(coordinates)
                .setHTML(`<pre>${description}</pre>`)
                .addTo(map);
        });

        // Change the cursor to a pointer when hovering over the layer
        map.on('mouseenter', 'geojson-layer', () => {
            map.getCanvas().style.cursor = 'pointer';
        });

        map.on('mouseleave', 'geojson-layer', () => {
            map.getCanvas().style.cursor = '';
        });

        map.resize();
    });
}

function updateGeoJson(map, geojsonData) {
    if (map.getSource('geojson-source')) {
        map.getSource('geojson-source').setData(geojsonData);
    }
}
