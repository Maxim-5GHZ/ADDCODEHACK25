import React, { useState } from 'react';
import { getArea } from 'ol/sphere';
import { transform } from 'ol/proj';
import FieldTypeSelector from './FieldTypeSelector';
import FieldForm from './FieldForm';
import OpenLayersMap from './OpenLayersMap';

function AddFieldOverlay({ isVisible, onClose, onSubmit }) {
  const [fieldType, setFieldType] = useState('polygon');
  const [fieldName, setFieldName] = useState('');
  const [radius, setRadius] = useState(100);
  const [geometry, setGeometry] = useState(null);
  const [area, setArea] = useState(null);

  const handleGeometryChange = (newGeometry, newRadius = null) => {
    setGeometry(newGeometry);
    
    if (newRadius !== null) {
      setRadius(Math.round(newRadius));
    }
    
    if (fieldType === 'polygon' && newGeometry && newGeometry.getType() === 'Polygon') {
      const areaValue = getArea(newGeometry);
      const areaHectares = (areaValue / 10000).toFixed(2);
      setArea(`${areaHectares} га`);
    } else if (fieldType === 'point' && newGeometry && newGeometry.getType() === 'Circle') {
      const areaValue = Math.PI * newGeometry.getRadius() * newGeometry.getRadius();
      const areaHectares = (areaValue / 10000).toFixed(2);
      setArea(`${areaHectares} га`);
    } else if (!newGeometry) {
      setArea(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!fieldName.trim()) {
      alert('Пожалуйста, введите название поля');
      return;
    }

    if (!geometry) {
      alert('Пожалуйста, выберите область на карте');
      return;
    }

    if (fieldType === 'polygon') {
      const coordinates = geometry.getCoordinates();
      const vertexCount = coordinates[0].length - 1;
      
      if (vertexCount < 3 || vertexCount > 5) {
        alert('Полигон должен содержать от 3 до 5 вершин');
        return;
      }
    }

    // Преобразуем геометрию в формат для сервера
    let areaOfInterest;
    
    try {
      if (fieldType === 'polygon') {
        const coordinates = geometry.getCoordinates()[0];
        // Преобразуем координаты из EPSG:3857 в EPSG:4326 (широта/долгота)
        const transformedCoordinates = coordinates.map(coord => 
          transform(coord, 'EPSG:3857', 'EPSG:4326')
        );
        
        areaOfInterest = {
          type: 'polygon',
          coordinates: transformedCoordinates
        };
      } else if (fieldType === 'point') {
        const center = geometry.getCenter();
        // Преобразуем центр из EPSG:3857 в EPSG:4326
        const transformedCenter = transform(center, 'EPSG:3857', 'EPSG:4326');
        
        areaOfInterest = {
          type: 'point_radius',
          lon: transformedCenter[0],
          lat: transformedCenter[1],
          radius_km: radius / 1000 // Конвертируем метры в километры
        };
      }

      onSubmit({
        type: fieldType,
        name: fieldName,
        radius: fieldType === 'point' ? radius : undefined,
        geometry: geometry,
        area: area,
        areaOfInterest: areaOfInterest
      });
    } catch (error) {
      console.error('Ошибка при преобразовании координат:', error);
      alert('Ошибка при обработке координат');
    }
  };

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) {
      handleClose();
    }
  };

  const handleClose = () => {
    setFieldName('');
    setRadius(100);
    setGeometry(null);
    setArea(null);
    onClose();
  };

  if (!isVisible) return null;

  return (
    <div 
      className="fixed inset-0 bg-[var(--overlay-bg)] flex items-center justify-center z-50 p-4"
      onClick={handleOverlayClick}
    >
      <div className="bg-white rounded-3xl w-[80vw] h-[80vh] flex flex-col lg:flex-row overflow-hidden">
        <div className="flex-1 p-6 min-h-[300px] lg:min-h-auto">
          <OpenLayersMap 
            fieldType={fieldType}
            onGeometryChange={handleGeometryChange}
            radius={radius}
          />
        </div>
        
        <div className="w-full lg:w-1/3 p-6 lg:p-8 flex flex-col">
          <div className="flex justify-between items-center mb-6 lg:mb-8">
            <h2 className="text-2xl lg:text-3xl font-bold text-[var(--neutral-dark-color)]">
              Добавить поле
            </h2>
            <button
              onClick={handleClose}
              className="text-3xl text-gray-500 hover:text-gray-700 transition-colors cursor-pointer"
            >
              ×
            </button>
          </div>

          <form onSubmit={handleSubmit} className="flex-1 flex flex-col">
            <FieldTypeSelector 
              fieldType={fieldType} 
              setFieldType={setFieldType} 
            />
            
            <FieldForm
              fieldType={fieldType}
              fieldName={fieldName}
              setFieldName={setFieldName}
              radius={radius}
              setRadius={setRadius}
              area={area}
            />
            
            <div className="mt-auto pt-6 lg:pt-8 flex gap-4">
              <button
                type="button"
                onClick={handleClose}
                className="flex-1 bg-[var(--neutral-color)] hover:bg-gray-200 transition-colors rounded-full py-4 text-xl font-semibold text-gray-700 cursor-pointer shadow-2xs"
              >
                Отмена
              </button>
              <button
                type="submit"
                className="flex-1 bg-[var(--accent-color)] hover:bg-[var(--accent-light-color)] transition-colors rounded-full py-4 text-xl font-semibold text-white cursor-pointer shadow-2xs"
              >
                Сохранить поле
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default AddFieldOverlay;