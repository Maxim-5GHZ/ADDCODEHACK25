import React, { useState } from 'react';
import { getArea, getDistance } from 'ol/sphere';
import FieldTypeSelector from './FieldTypeSelector';
import FieldForm from './FieldForm';
import OpenLayersMap from './OpenLayersMap';

function AddFieldOverlay({ isVisible, onClose, onSubmit }) {
  const [fieldType, setFieldType] = useState('polygon');
  const [fieldName, setFieldName] = useState('');
  const [radius, setRadius] = useState(100);
  const [geometry, setGeometry] = useState(null);
  const [area, setArea] = useState(null);
  const [perimeter, setPerimeter] = useState(null);

  const handleGeometryChange = (newGeometry) => {
    setGeometry(newGeometry);
    
    if (fieldType === 'polygon' && newGeometry.getType() === 'Polygon') {
      const areaValue = getArea(newGeometry);
      const areaHectares = (areaValue / 10000).toFixed(2);
      setArea(`${areaHectares} га`);
      
      const coordinates = newGeometry.getCoordinates()[0];
      let perimeterValue = 0;
      for (let i = 0; i < coordinates.length - 1; i++) {
        perimeterValue += getDistance(coordinates[i], coordinates[i + 1]);
      }
      setPerimeter(`${perimeterValue.toFixed(0)} м`);
    } else if (fieldType === 'point' && newGeometry.getType() === 'Circle') {
      const areaValue = Math.PI * newGeometry.getRadius() * newGeometry.getRadius();
      const areaHectares = (areaValue / 10000).toFixed(2);
      setArea(`${areaHectares} га`);
      setPerimeter(`${(2 * Math.PI * newGeometry.getRadius()).toFixed(0)} м`);
    }
  };

  const handleSubmit = (e) => {
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

    onSubmit({
      type: fieldType,
      name: fieldName,
      radius: fieldType === 'point' ? radius : undefined,
      geometry: geometry,
      area: area,
      perimeter: perimeter
    });
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
    setPerimeter(null);
    onClose();
  };

  if (!isVisible) return null;

  return (
    <div 
      className="fixed inset-0 bg-[var(--overlay-bg)] flex items-center justify-center z-50 p-4"
      onClick={handleOverlayClick}
    >
      <div className="bg-white rounded-3xl w-full max-w-6xl h-[80vh] flex flex-col lg:flex-row overflow-hidden">
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
              className="text-3xl text-gray-500 hover:text-gray-700 transition-colors"
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
              perimeter={perimeter}
            />
            
            <div className="mt-auto pt-6 lg:pt-8 flex gap-4">
              <button
                type="button"
                onClick={handleClose}
                className="flex-1 bg-gray-200 hover:bg-gray-300 transition-colors rounded-xl py-3 lg:py-4 text-lg lg:text-xl font-semibold text-gray-700"
              >
                Отмена
              </button>
              <button
                type="submit"
                className="flex-1 bg-[var(--accent-color)] hover:bg-[var(--accent-light-color)] transition-colors rounded-xl py-3 lg:py-4 text-lg lg:text-xl font-semibold text-white"
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
