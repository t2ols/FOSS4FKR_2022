import 'ol/ol.css';
import Map from 'ol/Map';
import OGCMapTile from 'ol/source/OGCMapTile';
import TileLayer from 'ol/layer/Tile';
import View from 'ol/View';

const map = new Map({
  target: 'map',
  layers: [
    new TileLayer({
      source: new OGCMapTile({
        url: 'https://maps.ecere.com/ogcapi/collections/blueMarble/map/tiles/WebMercatorQuad',
      }),
    }),
  ],
  view: new View({
    center: [0, 0],
    zoom: 1,
  }),
});
