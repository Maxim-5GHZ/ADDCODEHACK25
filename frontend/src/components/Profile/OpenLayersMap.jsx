import React, { useRef, useEffect, useState } from 'react';
import 'ol/ol.css';
import Map from 'ol/Map';
import View from 'ol/View';
import TileLayer from 'ol/layer/Tile';
import OSM from 'ol/source/OSM';
import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
import Draw from 'ol/interaction/Draw';
import Modify from 'ol/interaction/Modify';
import { Circle as CircleStyle, Fill, Stroke, Style } from 'ol/style';
import { getArea, getDistance } from 'ol/sphere';
import { Circle } from 'ol/geom';

function OpenLayersMap({ fieldType, onGeometryChange, radius }) {
  const mapRef = useRef(null);
  const mapInstance = useRef(null);
  const drawInteraction = useRef(null);
  const modifyInteraction = useRef(null);
  const vectorSource = useRef(new VectorSource());
  const [area, setArea] = useState(null);
  const [perimeter, setPerimeter] = useState(null);

  const getStyle = (feature) => {
    const geometry = feature.getGeometry();
    const type = geometry.getType();
    
    if (type === 'Point') {
      return new Style({
        image: new CircleStyle({
          radius: 6,
          fill: new Fill({
            color: '#009e4f'
          }),
          stroke: new Stroke({
            color: '#fff',
            width: 2
          })
        })
      });
    } else if (type === 'Polygon') {
      return new Style({
        fill: new Fill({
          color: 'rgba(0, 158, 79, 0.2)'
        }),
        stroke: new Stroke({
          color: '#009e4f',
          width: 2
        })
      });
    } else if (type === 'Circle') {
      return new Style({
        fill: new Fill({
          color: 'rgba(0, 158, 79, 0.1)'
        }),
        stroke: new Stroke({
          color: '#009e4f',
          width: 2,
          lineDash: [5, 5]
        })
      });
    }
  };

  useEffect(() => {
    if (!mapRef.current) return;

    const map = new Map({
      target: mapRef.current,
      layers: [
        new TileLayer({
          source: new OSM()
        }),
        new VectorLayer({
          source: vectorSource.current,
          style: getStyle
        })
      ],
      view: new View({
        center: [4188099.476, 7505781.418],
        zoom: 4
      })
    });

    const modify = new Modify({
      source: vectorSource.current
    });
    map.addInteraction(modify);
    modifyInteraction.current = modify;

    vectorSource.current.on('changefeature', (e) => {
      const feature = e.feature;
      if (feature) {
        updateMeasurements(feature);
      }
    });

    mapInstance.current = map;

    return () => {
      if (mapInstance.current) {
        mapInstance.current.setTarget(null);
      }
    };
  }, []);

  const updateMeasurements = (feature) => {
    const geometry = feature.getGeometry();
    
    if (geometry.getType() === 'Polygon') {
      const areaValue = getArea(geometry);
      const areaHectares = (areaValue / 10000).toFixed(2);
      setArea(`${areaHectares} га`);
      
      const coordinates = geometry.getCoordinates()[0];
      let perimeterValue = 0;
      for (let i = 0; i < coordinates.length - 1; i++) {
        perimeterValue += getDistance(coordinates[i], coordinates[i + 1]);
      }
      setPerimeter(`${perimeterValue.toFixed(0)} м`);
      
      if (onGeometryChange) {
        onGeometryChange(geometry);
      }
    } else if (geometry.getType() === 'Circle') {
      const radiusValue = geometry.getRadius();
      const areaValue = Math.PI * radiusValue * radiusValue;
      const areaHectares = (areaValue / 10000).toFixed(2);
      setArea(`${areaHectares} га`);
      setPerimeter(`${(2 * Math.PI * radiusValue).toFixed(0)} м`);
      
      if (onGeometryChange) {
        onGeometryChange(geometry);
      }
    }
  };

  useEffect(() => {
    if (!mapInstance.current) return;

    if (drawInteraction.current) {
      mapInstance.current.removeInteraction(drawInteraction.current);
      drawInteraction.current = null;
    }

    if (fieldType === 'polygon') {
      drawInteraction.current = new Draw({
        source: vectorSource.current,
        type: 'Polygon',
        maxPoints: 5,
        style: new Style({
          fill: new Fill({
            color: 'rgba(0, 158, 79, 0.2)'
          }),
          stroke: new Stroke({
            color: '#009e4f',
            width: 2
          })
        })
      });

      drawInteraction.current.on('drawend', (event) => {
        const feature = event.feature;
        updateMeasurements(feature);
      });

      mapInstance.current.addInteraction(drawInteraction.current);
    } else if (fieldType === 'point') {
      drawInteraction.current = new Draw({
        source: vectorSource.current,
        type: 'Point',
        style: new Style({
          image: new CircleStyle({
            radius: 6,
            fill: new Fill({
              color: '#009e4f'
            }),
            stroke: new Stroke({
              color: '#fff',
              width: 2
            })
          })
        })
      });

      drawInteraction.current.on('drawend', (event) => {
        const feature = event.feature;
        const point = feature.getGeometry();
        
        const circle = new Circle(point.getCoordinates(), radius || 100);
        const circleFeature = new ol.Feature({
          geometry: circle,
          name: 'radius_circle'
        });
        
        vectorSource.current.addFeature(circleFeature);
        updateMeasurements(circleFeature);
      });

      mapInstance.current.addInteraction(drawInteraction.current);
    }
  }, [fieldType, onGeometryChange]);

  useEffect(() => {
    if (fieldType === 'point' && radius) {
      const features = vectorSource.current.getFeatures();
      features.forEach(feature => {
        const geometry = feature.getGeometry();
        if (geometry.getType() === 'Circle') {
          geometry.setRadius(radius);
          updateMeasurements(feature);
        }
      });
    }
  }, [radius, fieldType]);

  return (
    <div 
      ref={mapRef} 
      className="w-full h-full rounded-xl overflow-hidden"
      style={{ minHeight: '400px' }}
    />
  );
}

export default OpenLayersMap;
