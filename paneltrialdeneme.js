import maplibregl from 'https://cdn.jsdelivr.net/npm/maplibre-gl@4.7.1/+esm';
// import mapboxGlArcgisFeatureserver from 'https://cdn.jsdelivr.net/npm/mapbox-gl-arcgis-featureserver@0.0.8/+esm';

export function render({ model, el }) {
  const map = new maplibregl.Map({
    container: el,
    style: model.tile_url,
    center: model.center,
    zoom: model.zoom,
    pitch: model.pitch,
    bearing: model.bearing,
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

  const arcgisLayerButton2 = document.createElement('button');
  arcgisLayerButton2.textContent = '2. ArcGIS Katmanı';
  arcgisLayerButton2.onclick = () => {
    model.show_arcgis_layer2 = !model.show_arcgis_layer2;
  };
  controlsContainer.appendChild(arcgisLayerButton2);

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
          paint: {
            'fill-color': '#ff0000',
            'fill-opacity': 0.5
          }
        });
      }

      const popup = new maplibregl.Popup({
        closeButton: true,
        closeOnClick: false,
      });

      arcgisLayerButton.onclick = () => {
        model.show_arcgis_layer = !model.show_arcgis_layer;
    
        // Eğer kaynak haritaya eklenmemişse, ekleyip sonra görünürlüğü ayarlayın
        if (model.show_arcgis_layer && !map.getSource("trailheads")) {
            fetch("https://akomcbs.ibb.istanbul/server/rest/services/Hosted/sensor/FeatureServer/0/query?f=geojson&where=1=1&token=" + model.token)
                .then(response => response.json())
                .then(data => {
                  console.log(data)
                    map.addSource("trailheads", {
                        type: "geojson",
                        data: data,
                    });
    
                    map.addLayer({
                        id: "arcgis-layer",
                        type: "circle",
                        source: "trailheads",
                        paint: {
                            "circle-color": "#45a6b7",
                            "circle-stroke-width": 0.5,
                            "circle-stroke-color": "white",
                        }
                    });
    
                    // İlk eklemede, görünürlüğü kapalı yapın.
                    map.setLayoutProperty("arcgis-layer", "visibility", model.show_arcgis_layer ? "visible" : "none");
                })
                .catch(error => {
                    console.error("ArcGIS katmanı yüklenirken hata oluştu:", error);
                });
        } 
        else if (map.getSource("trailheads")) {
            // Eğer kaynak zaten eklenmişse, sadece görünürlüğü ayarla
            map.setLayoutProperty("arcgis-layer", "visibility", model.show_arcgis_layer ? "visible" : "none");
        }
      };

      arcgisLayerButton2.onclick = () => {
        model.show_arcgis_layer2 = !model.show_arcgis_layer2;
    
        // Eğer kaynak haritaya eklenmemişse, ekleyip sonra görünürlüğü ayarlayın
        if (model.show_arcgis_layer2 && !map.getSource("trailheads2")) {
            fetch("https://akomcbs.ibb.istanbul/server/rest/services/Hosted/depremler/FeatureServer/0/query?f=geojson&where=1=1&token=" + model.token)
                .then(response2 => response2.json())
                .then(data => {
                    map.addSource("trailheads2", {
                        type: "geojson",
                        data: data,
                    });
    
                    map.addLayer({
                        id: "arcgis-layer2",
                        type: "circle",
                        source: "trailheads2",
                        paint: {
                            "circle-color": "red",
                            "circle-stroke-width": 0.5,
                            "circle-stroke-color": "white",
                        }
                    });

                    map.on('click', 'arcgis-layer2', (e) => {
                      const properties = e.features[0];
                      const description = `
                        <strong>Coordinates :</strong> ${properties.geometry.coordinates} <br>
                      `;
            
                      // Pop-up penceresini ayarlayın ve haritaya ekleyin
                      popup.setLngLat(e.lngLat)
                        .setHTML(description)
                        .addTo(map);
                    });
    
                    // İlk eklemede, görünürlüğü kapalı yapın.
                    map.setLayoutProperty("arcgis-layer2", "visibility", model.show_arcgis_layer2 ? "visible" : "none");
                })
                .catch(error => {
                    console.error("ArcGIS2 katmanı yüklenirken hata oluştu:", error);
                });
        } 
        else if (map.getSource("trailheads2")) {
            // Eğer kaynak zaten eklenmişse, sadece görünürlüğü ayarla
            map.setLayoutProperty("arcgis-layer2", "visibility", model.show_arcgis_layer2 ? "visible" : "none");
        }
      };
    

      if (!map.getSource('openmaptiles')) {
        map.addSource('openmaptiles', {
          url: 'https://api.maptiler.com/tiles/v3/tiles.json?key=ka2CI0XYdBCZt32lmrGA',
          type: 'vector',
        });

        map.addLayer({
          id: '3d-buildings',
          source: 'openmaptiles',
          'source-layer': 'building',
          type: 'fill-extrusion',
          minzoom: 15,
          paint: {
            'fill-extrusion-color': '#aaa',
            'fill-extrusion-height': ['interpolate', ['linear'], ['zoom'], 15, 0, 16, ['get', 'render_height']],
            'fill-extrusion-base': ['get', 'render_min_height'],
            'fill-extrusion-opacity': 0.6
          }
        });
      }

      map.setLayoutProperty('geojson-layer', 'visibility', model.show_first_layer ? 'visible' : 'none');
      map.setLayoutProperty('geojson-layer-2', 'visibility', model.show_second_layer ? 'visible' : 'none');
      // map.setLayoutProperty('arcgis-layer2', 'visibility', model.show_arcgis_layer2 ? 'visible' : 'none');
    };

    addLayers();

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

    model.on('change:show_first_layer', () => {
      map.setLayoutProperty('geojson-layer', 'visibility', model.show_first_layer ? 'visible' : 'none');
    });

    model.on('change:show_second_layer', () => {
      map.setLayoutProperty('geojson-layer-2', 'visibility', model.show_second_layer ? 'visible' : 'none');
    });

    // model.on('change:show_arcgis_layer2', () => {
    //   map.setLayoutProperty('arcgis-layer2', 'visibility', model.show_arcgis_layer2 ? 'visible' : 'none');
    // });

  });
}
