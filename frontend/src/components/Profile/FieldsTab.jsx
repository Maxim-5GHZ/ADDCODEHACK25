import React, { useState, useEffect } from 'react';
import AddFieldOverlay from './AddFieldOverlay';
import { getFieldsList, saveField, deleteField } from '../../utils/fetch';
import { getCookie } from '../../utils/cookies';
import FieldDetailsOverlay from './FieldDetailsOverlay';

function FieldsTab() {
  const [showAddFieldOverlay, setShowAddFieldOverlay] = useState(false);
  const [showFieldDetailsOverlay, setShowFieldDetailsOverlay] = useState(false);
  const [selectedField, setSelectedField] = useState(null);
  const [fields, setFields] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const handleShowDetails = (field) => {
      setSelectedField(field);
      setShowFieldDetailsOverlay(true);
    };

  // Загрузка списка полей с сервера
  const loadFields = async () => {
    try {
      const token = getCookie('token');
      const response = await getFieldsList(token);
      
      if (response.ok) {
        const data = await response.json();
        if (data.status === 'success') {
          setFields(data.fields || []);
        } else {
          setError('Ошибка при загрузке полей');
        }
      } else {
        setError('Ошибка соединения с сервером');
      }
    } catch (error) {
      console.error('Ошибка при загрузке полей:', error);
      setError('Ошибка при загрузке полей');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFields();
  }, []);

  const handleAddFieldSubmit = async (fieldData) => {
    try {
      const token = getCookie('token');
      
      // Преобразуем геометрию в формат для сервера
      let areaOfInterest;
      
      if (fieldData.type === 'polygon') {
        // Для полигона получаем координаты и преобразуем их
        const coordinates = fieldData.geometry.getCoordinates()[0];
        areaOfInterest = JSON.stringify({
          type: 'polygon',
          coordinates: coordinates
        });
      } else if (fieldData.type === 'point') {
        // Для точки с радиусом
        const center = fieldData.geometry.getCenter();
        areaOfInterest = JSON.stringify({
          type: 'point_radius',
          lon: center[0],
          lat: center[1],
          radius_km: fieldData.radius / 1000 // Конвертируем метры в километры
        });
      }

      const response = await saveField(token, fieldData.name, areaOfInterest);
      
      if (response.ok) {
        const result = await response.json();
        if (result.status === 'success') {
          // Обновляем список полей
          await loadFields();
          setShowAddFieldOverlay(false);
        } else {
          alert(`Ошибка при сохранении поля: ${result.detail}`);
        }
      } else {
        alert('Ошибка соединения с сервером');
      }
    } catch (error) {
      console.error('Ошибка при сохранении поля:', error);
      alert('Ошибка при сохранении поля');
    }
  };

  const handleDeleteField = async (fieldId) => {
    if (window.confirm('Вы уверены, что хотите удалить это поле?')) {
      try {
        const token = getCookie('token');
        const response = await deleteField(fieldId, token);
        
        if (response.ok) {
          const result = await response.json();
          if (result.status === 'success') {
            // Обновляем список полей после удаления
            await loadFields();
          } else {
            alert(`Ошибка при удалении поля: ${result.detail}`);
          }
        } else {
          alert('Ошибка соединения с сервером');
        }
      } catch (error) {
        console.error('Ошибка при удалении поля:', error);
        alert('Ошибка при удалении поля');
      }
    }
  };

  if (loading) {
    return (
      <div className="container">
        <div className="text-3xl font-semibold mb-4">Загрузка полей...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container">
        <div className="text-3xl font-semibold mb-4 text-red-500">{error}</div>
        <button 
          onClick={loadFields}
          className="bg-[var(--accent-color)] hover:bg-[var(--accent-light-color)] mt-6
          transition-[background-color] duration-100 cursor-pointer rounded-full text-3xl px-5 py-4 text-[var(--neutral-color)]"
        >
          Попробовать снова
        </button>
      </div>
    );
  }

  return (
    <>
      <div className="container">
        <div className="text-3xl font-semibold mb-4">
          {fields.length === 0 ? "У вас ещё нет полей" : "Ваши поля:"}
        </div>
        <ul className="space-y-4 max-h-[40vh] overflow-y-auto">
          {fields.map(field => (
            <li key={field.id} className="bg-[#f6f6f6] rounded-xl px-6 py-4 flex justify-between items-center">
              <div>
                <span className="text-xl font-medium text-gray-900">{field.name}</span>
                {field.area_of_interest && (
                  <div className="text-sm text-gray-600 mt-1">
                    {field.area_of_interest.type === 'polygon' ? 'Полигон' : 'Окружность'}
                  </div>
                )}
              </div>
              <div className="flex gap-2">
                <button 
                  onClick={() => handleShowDetails(field)}
                  className="text-[var(--accent-color)] font-bold hover:underline text-lg cursor-pointer"
                >
                  Подробнее
                </button>
                <button 
                  onClick={() => handleDeleteField(field.id)}
                  className="text-red-500 font-bold hover:underline text-lg ml-4 cursor-pointer"
                >
                  Удалить
                </button>
              </div>
            </li>
          ))}
        </ul>
        <div>
          <button 
            onClick={() => setShowAddFieldOverlay(true)}
            className="bg-[var(--accent-color)] hover:bg-[var(--accent-light-color)] mt-6
            transition-[background-color] duration-100 cursor-pointer rounded-full text-3xl px-5 py-4 text-[var(--neutral-color)]"
          >
            Добавить поле
          </button>
        </div>
      </div>

      <AddFieldOverlay
        isVisible={showAddFieldOverlay}
        onClose={() => setShowAddFieldOverlay(false)}
        onSubmit={handleAddFieldSubmit}
      />

      <FieldDetailsOverlay
        isVisible={showFieldDetailsOverlay}
        onClose={() => setShowFieldDetailsOverlay(false)}
        field={selectedField}
      />
    </>
  );
}

export default FieldsTab;