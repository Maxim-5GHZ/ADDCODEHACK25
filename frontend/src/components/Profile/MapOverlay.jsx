import React, { useRef, useEffect, useState } from 'react';
import Map from 'ol/Map';
import View from 'ol/View';
import TileLayer from 'ol/layer/Tile';
import OSM from 'ol/source/OSM';
import XYZ from 'ol/source/XYZ';
import ImageLayer from 'ol/layer/Image';
import ImageStatic from 'ol/source/ImageStatic';
import { transformExtent, get as getProjection } from 'ol/proj';
import { getWidth } from 'ol/extent';
import ScaleLine from 'ol/control/ScaleLine';
import Zoom from 'ol/control/Zoom';
import FullScreen from 'ol/control/FullScreen';

function MapOverlay({ imageData, bounds, imageType }) {
  const mapRef = useRef(null);
  const mapInstance = useRef(null);
  const [tileSource, setTileSource] = useState('osm');
  const [isMapInitialized, setIsMapInitialized] = useState(false);
  const [showLegend, setShowLegend] = useState(false);

  // Определяем источники тайлов
  const tileSources = {
    osm: new OSM({
      attributions: ['OSM']
    }),
    satellite: new XYZ({
      url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
      attributions: ['Tiles &copy; Esri']
    })
  };

  // Функция для переключения тайлов
  const switchTileSource = (source) => {
    setTileSource(source);
    if (mapInstance.current) {
      const layers = mapInstance.current.getLayers();
      layers.setAt(0, new TileLayer({
        source: tileSources[source]
      }));
      mapInstance.current.updateSize();
    }
  };

  // Функция для приближения к участку
  const zoomToBounds = () => {
    if (!mapInstance.current || !bounds) return;
    
    const imageExtent = transformExtent(bounds.flat(), 'EPSG:4326', 'EPSG:3857');
    mapInstance.current.getView().fit(imageExtent, {
      padding: [20, 20, 20, 20],
      duration: 500
    });
  };

  // Создаем слой с изображением анализа
  const createImageLayer = () => {
    if (!imageData || !bounds) return null;

    // Преобразуем bounds в EPSG:3857
    const imageExtent = transformExtent(bounds.flat(), 'EPSG:4326', 'EPSG:3857');
    
    return new ImageLayer({
      source: new ImageStatic({
        url: `data:image/png;base64,${imageData}`,
        imageExtent: imageExtent,
        projection: 'EPSG:3857'
      }),
      opacity: 0.8
    });
  };

  // Инициализация карты
  useEffect(() => {
    if (!mapRef.current || !bounds || !imageData) return;

    const imageExtent = transformExtent(bounds.flat(), 'EPSG:4326', 'EPSG:3857');
    
    const map = new Map({
      target: mapRef.current,
      layers: [
        new TileLayer({
          source: tileSources[tileSource]
        }),
        createImageLayer()
      ],
      view: new View({
        projection: 'EPSG:3857',
        center: [4188099.476, 7505781.418], // Центр по умолчанию
        zoom: 7 // Zoom по умолчанию
      }),
      controls: [
        new Zoom(),
        new FullScreen(),
        new ScaleLine({
          units: 'metric'
        })
      ]
    });

    // Устанавливаем вид на область изображения при инициализации
    map.getView().fit(imageExtent, {
      padding: [20, 20, 20, 20],
      duration: 500
    });

    mapInstance.current = map;
    setIsMapInitialized(true);

    return () => {
      if (mapInstance.current) {
        mapInstance.current.setTarget(null);
        mapInstance.current = null;
      }
    };
  }, []);

  // Обновление карты при изменении данных
  useEffect(() => {
    if (!mapInstance.current || !isMapInitialized || !imageData || !bounds) return;

    // Удаляем старый слой изображения
    const layers = mapInstance.current.getLayers();
    if (layers.getLength() > 1) {
      layers.removeAt(1);
    }

    // Добавляем новый слой изображения
    const imageLayer = createImageLayer();
    if (imageLayer) {
      layers.push(imageLayer);
    }

    mapInstance.current.updateSize();
  }, [imageData, bounds, imageType]);

  // Обновление базового слоя
  useEffect(() => {
    if (!mapInstance.current || !isMapInitialized) return;

    const layers = mapInstance.current.getLayers();
    layers.setAt(0, new TileLayer({
      source: tileSources[tileSource]
    }));
    mapInstance.current.updateSize();
  }, [tileSource]);

  if (!imageData || !bounds) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-gray-100 rounded-lg">
        <div className="text-lg md:text-xl text-gray-500 text-center px-4">Нет данных для отображения карты</div>
      </div>
    );
  }

  return (
    <div className="w-full h-full rounded-lg overflow-hidden relative">
      <div 
        ref={mapRef} 
        className="w-full h-full"
      />
      
      {/* Панель выбора типа карты */}
      <div className="absolute top-2 md:top-4 right-2 md:right-4 bg-white bg-opacity-90 p-1 md:p-2 rounded-lg shadow-md flex space-x-1 md:space-x-2">
        <button
          onClick={() => switchTileSource('osm')}
          className={`px-2 md:px-3 py-1 rounded text-sm md:text-md ${
            tileSource === 'osm' 
              ? 'bg-[var(--accent-color)] text-white' 
              : 'bg-gray-200 text-gray-700 cursor-pointer'
          }`}
        >
          Карта
        </button>
        <button
          onClick={() => switchTileSource('satellite')}
          className={`px-2 md:px-3 py-1 rounded text-sm md:text-md ${
            tileSource === 'satellite' 
              ? 'bg-[var(--accent-color)] text-white' 
              : 'bg-gray-200 text-gray-700 cursor-pointer'
          }`}
        >
          Спутник
        </button>
      </div>

      {/* Легенда и кнопка приближения */}
      <div className="absolute bottom-2 md:bottom-4 right-2 md:right-4 flex flex-col items-end space-y-2 md:space-y-3">
        {/* Кнопка приближения к участку */}
        <button
          onClick={zoomToBounds}
          className="bg-[var(--accent-color)] hover:bg-[var(--accent-light-color)] text-white px-3 md:px-4 py-2 rounded-lg shadow-md cursor-pointer transition-colors text-sm md:text-lg font-medium whitespace-nowrap"
        >
          Приблизить к участку
        </button>
        
        {/* Кнопка показа/скрытия легенды на мобильных */}
        <button
          onClick={() => setShowLegend(!showLegend)}
          className="md:hidden bg-white bg-opacity-90 hover:bg-opacity-100 text-gray-700 px-3 py-2 rounded-lg shadow-md cursor-pointer transition-colors text-sm font-medium"
        >
          {showLegend ? 'Скрыть легенду' : 'Показать легенду'}
        </button>
        
        {/* Легенда */}
        <div className={`bg-white bg-opacity-90 p-3 md:p-4 rounded-lg shadow-md max-w-xs ${showLegend ? 'block' : 'hidden md:block'}`}>
          <div className="text-base md:text-lg font-medium text-gray-700 mb-1 md:mb-2">
            {imageType === 'ndvi_overlay_image' ? 'NDVI карта' : 'Проблемные зоны'}
          </div>
          <div className="text-sm md:text-base text-gray-600">
            {imageType === 'ndvi_overlay_image' 
              ? 'Зеленый - высокая вегетация, Красный - низкая вегетация' 
              : 'Красный - проблемные зоны, Зеленый - нормальные зоны'}
          </div>
        </div>
      </div>

      {/* Дополнительные элементы для мобильных устройств */}
      <div className="absolute bottom-2 md:bottom-4 left-2 md:left-4 flex flex-col space-y-2">
        {/* Информация о типе карты для мобильных */}
        <div className="md:hidden bg-white bg-opacity-90 p-2 rounded-lg shadow-md">
          <div className="text-xs text-gray-600">
            {imageType === 'ndvi_overlay_image' ? 'NDVI' : 'Проблемные зоны'}
          </div>
        </div>
      </div>
    </div>
  );
}

export default MapOverlay;