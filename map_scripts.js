import mapboxgl from 'mapbox-gl';
import FeatureService from 'mapbox-gl-arcgis-featureserver';

const map = new mapboxgl.Map({
  container: 'map',
  style: 'https://api.maptiler.com/maps/basic-v2/style.json?key=ka2CI0XYdBCZt32lmrGA',
  center: [28.06, 41.77], 
  zoom: 10
});

map.on('load', () => {
  const fsSourceId = 'featureserver-src';

  const service = new FeatureService(fsSourceId, map, {
    url: 'https://portal.spatial.nsw.gov.au/server/rest/services/NSW_Administrative_Boundaries_Theme/FeatureServer/6'
  });

  map.addLayer({
    'id': 'fill-lyr',
    'source': fsSourceId,
    'type': 'fill',
    'paint': {
      'fill-opacity': 0.5,
      'fill-color': '#B42222'
    }
  });
});
