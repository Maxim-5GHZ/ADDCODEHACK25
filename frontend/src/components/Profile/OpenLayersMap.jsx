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
import { getArea } from 'ol/sphere';
import { Circle } from 'ol/geom';
import Feature from 'ol/Feature';

function OpenLayersMap({ fieldType, onGeometryChange, radius }) {
  const mapRef = useRef(null);
  const mapInstance = useRef(null);
  const drawInteraction = useRef(null);
  const modifyInteraction = useRef(null);
  const vectorSource = useRef(new VectorSource());
  const [area, setArea] = useState(null);
  const [hasGeometry, setHasGeometry] = useState(false);
  const [isMapInitialized, setIsMapInitialized] = useState(false);
  const isUpdatingFromMap = useRef(false);

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

  // Функция для проверки количества вершин в полигоне
  const getVertexCount = (geometry) => {
    if (geometry.getType() === 'Polygon') {
      const coordinates = geometry.getCoordinates()[0];
      return coordinates.length - 1; // -1 потому что первая и последняя точка одинаковы
    }
    return 0;
  };

  // Функция для очистки выделения
  const clearSelection = () => {
    vectorSource.current.clear();
    setHasGeometry(false);
    setArea(null);
    if (onGeometryChange) {
      onGeometryChange(null);
    }
    
    // Восстанавливаем возможность рисования только если карта существует
    if (mapInstance.current) {
      if (drawInteraction.current) {
        mapInstance.current.removeInteraction(drawInteraction.current);
        drawInteraction.current = null;
      }
      setupDrawInteraction();
    }
  };

  const updateMeasurements = (feature, isFromMapInteraction = false) => {
    const geometry = feature.getGeometry();
    
    if (geometry.getType() === 'Polygon') {
      const areaValue = getArea(geometry);
      const areaHectares = (areaValue / 10000).toFixed(2);
      setArea(`${areaHectares} га`);
      
      if (onGeometryChange) {
        onGeometryChange(geometry);
      }
    } else if (geometry.getType() === 'Circle') {
      const radiusValue = geometry.getRadius();
      const areaValue = Math.PI * radiusValue * radiusValue;
      const areaHectares = (areaValue / 10000).toFixed(2);
      setArea(`${areaHectares} га`);
      
      if (onGeometryChange && isFromMapInteraction) {
        onGeometryChange(geometry, radiusValue);
      } else if (onGeometryChange) {
        onGeometryChange(geometry);
      }
    }
  };

  // Функция для завершения рисования по Enter
  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && drawInteraction.current) {
      // Завершаем рисование
      drawInteraction.current.finishDrawing();
    }
  };

  const setupDrawInteraction = () => {
    if (!mapInstance.current || hasGeometry) return;

    if (drawInteraction.current) {
      mapInstance.current.removeInteraction(drawInteraction.current);
      drawInteraction.current = null;
    }

    // Убедимся, что элемент карты существует
    const mapElement = mapInstance.current.getTargetElement();
    if (!mapElement) return;

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
        setHasGeometry(true);
        updateMeasurements(feature, true);
        
        // Удаляем взаимодействие рисования после создания полигона
        if (drawInteraction.current) {
          mapInstance.current.removeInteraction(drawInteraction.current);
          drawInteraction.current = null;
        }

        // Удаляем обработчик нажатия клавиш
        mapElement.removeEventListener('keydown', handleKeyPress);
      });

      // Добавляем обработчик нажатия клавиш
      mapElement.addEventListener('keydown', handleKeyPress);
      
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
        
        // Создаем круг с указанным радиусом
        const circle = new Circle(point.getCoordinates(), radius || 100);
        const circleFeature = new Feature({
          geometry: circle,
          name: 'radius_circle'
        });
        
        // Удаляем точку и добавляем круг
        vectorSource.current.clear();
        vectorSource.current.addFeature(circleFeature);
        
        setHasGeometry(true);
        updateMeasurements(circleFeature, true);
        
        // Удаляем взаимодействие рисования после создания круга
        if (drawInteraction.current) {
          mapInstance.current.removeInteraction(drawInteraction.current);
          drawInteraction.current = null;
        }
      });

      mapInstance.current.addInteraction(drawInteraction.current);
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

    // Создаем модификацию с ограничением на добавление вершин
    const modify = new Modify({
      source: vectorSource.current,
      insertVertexCondition: (event) => {
        // Проверяем, можно ли добавлять вершины
        const features = event.features;
        if (features.getLength() > 0) {
          const feature = features.item(0);
          const geometry = feature.getGeometry();
          
          // Для полигонов ограничиваем количество вершин до 5
          if (geometry.getType() === 'Polygon') {
            const vertexCount = getVertexCount(geometry);
            return vertexCount < 5; // Разрешаем добавление только если вершин меньше 5
          }
        }
        return true; // Для других типов геометрии разрешаем добавление
      }
    });
    
    modify.on('modifyend', (event) => {
      event.features.forEach(feature => {
        updateMeasurements(feature, true);
      });
    });
    
    map.addInteraction(modify);
    modifyInteraction.current = modify;

    mapInstance.current = map;
    setIsMapInitialized(true);

    return () => {
      if (mapInstance.current) {
        // Удаляем обработчик клавиш
        const mapElement = mapInstance.current.getTargetElement();
        if (mapElement) {
          mapElement.removeEventListener('keydown', handleKeyPress);
        }
        mapInstance.current.setTarget(null);
        mapInstance.current = null;
      }
      setIsMapInitialized(false);
    };
  }, []);

  useEffect(() => {
    if (isMapInitialized) {
      setupDrawInteraction();
    }
  }, [fieldType, hasGeometry, isMapInitialized]);

  useEffect(() => {
    if (fieldType === 'point' && radius && hasGeometry && isMapInitialized) {
      const features = vectorSource.current.getFeatures();
      const circleFeature = features.find(feature => 
        feature.getGeometry().getType() === 'Circle'
      );
      
      if (circleFeature) {
        const geometry = circleFeature.getGeometry();
        geometry.setRadius(radius);
        updateMeasurements(circleFeature, false);
      }
    }
  }, [radius, fieldType, hasGeometry, isMapInitialized]);

  return (
    <div className="w-full h-full rounded-xl overflow-hidden relative" style={{ minHeight: '400px' }}>
      <div 
        ref={mapRef} 
        className="w-full h-full cursor-pointer"
        tabIndex={0} // Добавляем tabIndex для возможности фокуса и обработки клавиш
      />
      {hasGeometry && (
        <button
          onClick={clearSelection}
          className="absolute bottom-4 left-4 bg-[var(--accent-color)] hover:bg-[var(--accent-light-color)] text-white px-6 py-3 rounded-full text-xl shadow-2xs cursor-pointer transition-colors"
        >
          Очистить выделение
        </button>
      )}
    </div>
  );
}

export default OpenLayersMap;