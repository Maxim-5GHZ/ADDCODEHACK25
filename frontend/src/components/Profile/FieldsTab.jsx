import React, { useState, useEffect } from 'react';
import { getFieldsList, saveField, deleteField, performAnalysis } from '../../utils/fetch';
import { getCookie } from '../../utils/cookies';
import AddFieldOverlay from './AddFieldOverlay';

function FieldsTab({ setActiveTab }) {
  const [showAddFieldOverlay, setShowAddFieldOverlay] = useState(false);
  const [fields, setFields] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [analyzingField, setAnalyzingField] = useState(null);
  const [showAnalysisComplete, setShowAnalysisComplete] = useState(false);
  const [lastAnalysisId, setLastAnalysisId] = useState(null);

  console.log('FieldsTab: Рендер компонента');

  // Загрузка списка полей с сервера
  const loadFields = async () => {
    console.log('FieldsTab: Начало загрузки полей');
    try {
      const token = getCookie('token');
      const response = await getFieldsList(token);
      
      if (response.ok) {
        const data = await response.json();
        if (data.status === 'success') {
          setFields(data.fields || []);
          console.log('FieldsTab: Поля успешно загружены', { count: data.fields?.length });
        } else {
          setError('Ошибка при загрузке полей');
          console.error('FieldsTab: Ошибка в статусе ответа полей', data);
        }
      } else {
        setError('Ошибка соединения с сервером');
        console.error('FieldsTab: Ошибка HTTP при загрузке полей', response.status);
      }
    } catch (error) {
      console.error('FieldsTab: Исключение при загрузке полей:', error);
      setError('Ошибка при загрузке полей');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFields();
  }, []);

  const handleAddFieldSubmit = async (fieldData) => {
    console.log('FieldsTab: Сохранение нового поля', { fieldName: fieldData.name, type: fieldData.type });
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
          console.log('FieldsTab: Поле успешно сохранено');
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
      console.log('FieldsTab: Удаление поля', { fieldId });
      try {
        const token = getCookie('token');
        const response = await deleteField(fieldId, token);
        
        if (response.ok) {
          const result = await response.json();
          if (result.status === 'success') {
            // Обновляем список полей после удаления
            await loadFields();
            console.log('FieldsTab: Поле успешно удалено');
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

  const handleAnalyzeField = async (field) => {
    console.log('FieldsTab: Запуск анализа поля', { fieldId: field.id, fieldName: field.name });
    
    try {
      setAnalyzingField(field.id);
      const token = getCookie('token');
      
      // Получаем даты (сегодня и 30 дней назад)
      const endDate = new Date().toISOString().split('T')[0];
      const startDate = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
      
      console.log('FieldsTab: Параметры анализа', { startDate, endDate, fieldType: field.area_of_interest.type });
      
      let response;
      
      if (field.area_of_interest.type === 'point_radius') {
        console.log('FieldsTab: Анализ по точке с радиусом', field.area_of_interest);
        response = await performAnalysis(
          token, 
          startDate, 
          endDate, 
          {
            lon: field.area_of_interest.lon,
            lat: field.area_of_interest.lat,
            radius_km: field.area_of_interest.radius_km
          }
        );
      } else if (field.area_of_interest.type === 'polygon') {
        console.log('FieldsTab: Анализ по полигону', { coordinatesCount: field.area_of_interest.coordinates?.length });
        response = await performAnalysis(
          token,
          startDate,
          endDate,
          {
            polygonCoords: field.area_of_interest.coordinates
          }
        );
      }
      
      console.log('FieldsTab: Ответ от сервера на анализ', { status: response?.status });
      
      if (response.ok) {
        const result = await response.json();
        console.log('FieldsTab: Результат анализа', { status: result.status, analysisId: result.analysis_id });
        
        if (result.status === 'success') {
          setLastAnalysisId(result.analysis_id);
          setShowAnalysisComplete(true);
          console.log('FieldsTab: Анализ успешно завершен', { analysisId: result.analysis_id });
        } else {
          alert(`Ошибка при выполнении анализа: ${result.detail}`);
        }
      } else {
        alert('Ошибка соединения с сервером при выполнении анализа');
      }
    } catch (error) {
      console.error('FieldsTab: Исключение при выполнении анализа:', error);
      alert('Ошибка при выполнении анализа');
    } finally {
      setAnalyzingField(null);
    }
  };

  const handleGoToAnalyses = () => {
    console.log('FieldsTab: Переход к анализам');
    setShowAnalysisComplete(false);
    setActiveTab('analyses');
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
                <span className="text-2xl font-medium text-gray-900">{field.name}</span>
                {field.area_of_interest && (
                  <div className="text-xl text-gray-600 mt-1">
                    {field.area_of_interest.type === 'polygon' ? 'Полигон' : 'Окружность'}
                  </div>
                )}
              </div>
              <div className="flex gap-4">
                <button 
                  onClick={() => handleAnalyzeField(field)}
                  disabled={analyzingField === field.id}
                  className="bg-[var(--accent-color)] hover:bg-[var(--accent-light-color)] disabled:bg-gray-400
                  transition-[background-color] duration-100 cursor-pointer rounded-full text-2xl px-5 py-3 text-white"
                >
                  {analyzingField === field.id ? 'Анализ...' : 'Анализировать'}
                </button>
                <button 
                  onClick={() => handleDeleteField(field.id)}
                  className="text-red-500 font-bold hover:underline text-2xl cursor-pointer"
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

      {/* Модальное окно завершения анализа */}
      {showAnalysisComplete && (
        <div className="fixed inset-0 bg-[var(--overlay-bg)] flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-3xl p-8 max-w-md w-full">
            <h3 className="text-3xl font-bold mb-4 text-[var(--neutral-dark-color)]">
              Анализ завершен!
            </h3>
            <p className="text-2xl text-gray-700 mb-6">
              Анализ поля успешно выполнен. Вы можете просмотреть результаты во вкладке "Анализы".
            </p>
            <div className="flex gap-4">
              <button
                onClick={() => setShowAnalysisComplete(false)}
                className="flex-1 bg-gray-200 hover:bg-gray-300 transition-colors rounded-full py-3 text-2xl font-semibold text-gray-700 cursor-pointer"
              >
                Остаться
              </button>
              <button
                onClick={handleGoToAnalyses}
                className="flex-1 bg-[var(--accent-color)] hover:bg-[var(--accent-light-color)] transition-colors rounded-full py-3 text-2xl font-semibold text-white cursor-pointer"
              >
                Перейти к анализам
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Оверлей добавления поля - ВОЗВРАЩАЕМ! */}
      <AddFieldOverlay
        isVisible={showAddFieldOverlay}
        onClose={() => setShowAddFieldOverlay(false)}
        onSubmit={handleAddFieldSubmit}
      />
    </>
  );
}

export default FieldsTab;