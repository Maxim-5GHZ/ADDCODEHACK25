import React, { useRef, useEffect, useState } from 'react';
import 'ol/ol.css';
import Map from 'ol/Map';
import View from 'ol/View';
import TileLayer from 'ol/layer/Tile';
import OSM from 'ol/source/OSM';
import XYZ from 'ol/source/XYZ';
import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
import Draw from 'ol/interaction/Draw';
import Modify from 'ol/interaction/Modify';
import { Circle as CircleStyle, Fill, Stroke, Style, Text } from 'ol/style';
import { getArea, getLength } from 'ol/sphere';
import { Circle } from 'ol/geom';
import Feature from 'ol/Feature';
import ScaleLine from 'ol/control/ScaleLine';
import Zoom from 'ol/control/Zoom';
import Rotate from 'ol/control/Rotate';
import FullScreen from 'ol/control/FullScreen';
import MousePosition from 'ol/control/MousePosition';
import { createStringXY } from 'ol/coordinate';
import Overlay from 'ol/Overlay';

function OpenLayersMap({ fieldType, onGeometryChange, radius }) {
  const mapRef = useRef(null);
  const mapInstance = useRef(null);
  const drawInteraction = useRef(null);
  const modifyInteraction = useRef(null);
  const vectorSource = useRef(new VectorSource());
  const [area, setArea] = useState(null);
  const [perimeter, setPerimeter] = useState(null);
  const [hasGeometry, setHasGeometry] = useState(false);
  const [isMapInitialized, setIsMapInitialized] = useState(false);
  const [tileSource, setTileSource] = useState('osm'); // 'osm', 'satellite', 'terrain'
  const popupRef = useRef(null);
  const popupContentRef = useRef(null);
  const isUpdatingFromMap = useRef(false);

  // Определяем источники тайлов
  const tileSources = {
    osm: new OSM({
      attributions: ['OSM']
    }),
    satellite: new XYZ({
      url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
      attributions: ['Tiles &copy; Esri']
    }),
    terrain: new XYZ({
      url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Shaded_Relief/MapServer/tile/{z}/{y}/{x}',
      attributions: ['Tiles &copy; Esri']
    })
  };

  // Получаем текущий источник тайлов
  const getCurrentTileSource = () => {
    return tileSources[tileSource];
  };

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
    setPerimeter(null);
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
      const perimeterValue = getLength(geometry);
      const areaHectares = (areaValue / 10000).toFixed(2);
      const perimeterKm = (perimeterValue / 1000).toFixed(2);
      
      setArea(`${areaHectares} га`);
      setPerimeter(`${perimeterKm} км`);
      
      if (onGeometryChange) {
        onGeometryChange(geometry);
      }
    } else if (geometry.getType() === 'Circle') {
      const radiusValue = geometry.getRadius();
      const areaValue = Math.PI * radiusValue * radiusValue;
      const perimeterValue = 2 * Math.PI * radiusValue;
      const areaHectares = (areaValue / 10000).toFixed(2);
      const perimeterKm = (perimeterValue / 1000).toFixed(2);
      
      setArea(`${areaHectares} га`);
      setPerimeter(`${perimeterKm} км`);
      
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

  // Функция для переключения тайлов
  const switchTileSource = (source) => {
    setTileSource(source);
    if (mapInstance.current) {
      const layers = mapInstance.current.getLayers();
      // Заменяем базовый слой (первый слой)
      layers.setAt(0, new TileLayer({
        source: tileSources[source]
      }));
      
      // Принудительно обновляем карту
      mapInstance.current.updateSize();
      
      // Восстанавливаем фокус на элементе карты
      setTimeout(() => {
        if (mapRef.current) {
          mapRef.current.focus();
        }
      }, 100);
    }
  };

  // Функция для восстановления взаимодействия с картой
  const restoreMapInteractions = () => {
    if (mapInstance.current && mapRef.current) {
      // Принудительно обновляем размер карты
      mapInstance.current.updateSize();
      
      // Восстанавливаем фокус
      mapRef.current.focus();
      
      // Перерисовываем карту
      mapInstance.current.render();
    }
  };

  useEffect(() => {
    if (!mapRef.current) return;

    const map = new Map({
      target: mapRef.current,
      layers: [
        new TileLayer({
          source: getCurrentTileSource()
        }),
        new VectorLayer({
          source: vectorSource.current,
          style: getStyle
        })
      ],
      view: new View({
        center: [4188099.476, 7505781.418],
        zoom: 7
      }),
      controls: [
        // Стандартные элементы управления
        new Zoom(),
        new Rotate(),
        new FullScreen(),
        // Линейка масштаба посередине внизу
        new ScaleLine({
          units: 'metric',
          className: 'ol-scale-line-bottom-center'
        }),
        // Отображение координат курсора посередине сверху
        new MousePosition({
          coordinateFormat: createStringXY(4),
          projection: 'EPSG:4326',
          className: 'custom-mouse-position-top',
          placeholder: 'Наведите курсор на карту'
        })
      ]
    });

    // Создаем попап для отображения информации
    const popup = new Overlay({
      element: popupRef.current,
      positioning: 'bottom-center',
      stopEvent: false,
      offset: [0, -10]
    });
    map.addOverlay(popup);

    // Обработчик движения курсора для попапа
    map.on('pointermove', function (evt) {
      const feature = map.forEachFeatureAtPixel(evt.pixel, function (feature) {
        return feature;
      });
      
      if (feature) {
        const geometry = feature.getGeometry();
        const type = geometry.getType();
        
        let content = '';
        if (type === 'Polygon') {
          const areaValue = getArea(geometry);
          const areaHectares = (areaValue / 10000).toFixed(2);
          content = `Площадь: ${areaHectares} га`;
        } else if (type === 'Circle') {
          const radiusValue = geometry.getRadius();
          const areaValue = Math.PI * radiusValue * radiusValue;
          const areaHectares = (areaValue / 10000).toFixed(2);
          content = `Радиус: ${(radiusValue / 1000).toFixed(2)} км, Площадь: ${areaHectares} га`;
        }
        
        if (popupContentRef.current) {
          popupContentRef.current.innerHTML = content;
          popup.setPosition(evt.coordinate);
        }
      } else {
        popup.setPosition(undefined);
      }
    });

    // Обработчик клика по карте для восстановления взаимодействия
    map.on('click', function() {
      restoreMapInteractions();
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
        onClick={restoreMapInteractions} // Дополнительный обработчик клика
      />
      
      {/* Попап для отображения информации о геометрии */}
      <div ref={popupRef} className="ol-popup absolute bg-white p-2 rounded shadow-lg text-sm hidden">
        <div ref={popupContentRef}></div>
      </div>
      
      {/* Информационная панель */}
      {area && (
        <div className="absolute top-4 left-4 bg-white bg-opacity-90 p-3 rounded-lg shadow-md">
          <div className="text-sm text-gray-700">
            <div className="font-medium">Площадь: <span className="text-green-600">{area}</span></div>
            {perimeter && (
              <div className="font-medium">Периметр: <span className="text-green-600">{perimeter}</span></div>
            )}
          </div>
        </div>
      )}
      
      {/* Панель выбора типа карты */}
      <div className="absolute top-4 right-4 bg-white bg-opacity-90 p-2 rounded-lg shadow-md flex space-x-2">
        <button
          onClick={() => switchTileSource('osm')}
          className={`px-3 py-1 rounded text-md ${tileSource === 'osm' ? 'bg-[var(--accent-color)] text-white' : 'bg-gray-200 text-gray-700 cursor-pointer'}`}
        >
          Карта
        </button>
        <button
          onClick={() => switchTileSource('satellite')}
          className={`px-3 py-1 rounded text-md ${tileSource === 'satellite' ? 'bg-[var(--accent-color)] text-white' : 'bg-gray-200 text-gray-700 cursor-pointer'}`}
        >
          Спутник
        </button>
        <button
          onClick={() => switchTileSource('terrain')}
          className={`px-3 py-1 rounded text-md ${tileSource === 'terrain' ? 'bg-[var(--accent-color)] text-white' : 'bg-gray-200 text-gray-700 cursor-pointer'}`}
        >
          Рельеф
        </button>
      </div>
      
      {hasGeometry && (
        <button
          onClick={clearSelection}
          className="absolute bottom-4 left-4 bg-[var(--accent-color)] hover:bg-[var(--accent-light-color)] text-white px-6 py-3 rounded-full text-xl shadow-2xs cursor-pointer transition-colors"
        >
          Очистить выделение
        </button>
      )}

      {/* CSS для позиционирования и стилизации элементов */}
      <style>{`
        .ol-scale-line-bottom-center {
          position: absolute;
          bottom: 8px;
          left: 50%;
          transform: translateX(-50%);
          background: rgba(255,255,255,0.8);
          padding: 2px 8px;
          border-radius: 4px;
        }
        .ol-scale-line-inner {
          border: 2px solid #333;
          border-top: none;
          color: #333;
          font-size: 12px;
          text-align: center;
          margin: 1px;
          will-change: contents, width;
        }
        .custom-mouse-position-top {
          position: absolute;
          top: 8px;
          left: 50%;
          transform: translateX(-50%);
          background: rgba(255,255,255,0.8);
          padding: 4px 12px;
          border-radius: 4px;
          font-size: 14px;
          color: #333;
        }
      `}</style>
    </div>
  );
}

export default OpenLayersMap;