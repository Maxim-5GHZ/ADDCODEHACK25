import React, { useState, useEffect } from 'react';
import { getCookie } from '../../utils/cookies';
import { performAnalysis, getAnalysisList, getAnalysisById, getAnalysisRecommendations } from '../../utils/fetch';

function FieldDetailsOverlay({ isVisible, onClose, field }) {
  const [currentAnalysis, setCurrentAnalysis] = useState(null);
  const [analysesList, setAnalysesList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedAnalysisId, setSelectedAnalysisId] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [loadingRecommendations, setLoadingRecommendations] = useState(false);

  console.log('FieldDetailsOverlay: Рендер компонента', { isVisible, field, currentAnalysis });

  // Загрузка списка анализов при открытии
  useEffect(() => {
    if (isVisible) {
      console.log('FieldDetailsOverlay: Открытие оверлея, загрузка списка анализов');
      loadAnalysesList();
    } else {
      console.log('FieldDetailsOverlay: Закрытие оверлея, сброс состояния');
      setCurrentAnalysis(null);
      setSelectedAnalysisId(null);
      setRecommendations(null);
    }
  }, [isVisible]);

  const loadAnalysesList = async () => {
    console.log('FieldDetailsOverlay: Начало загрузки списка анализов');
    try {
      const token = getCookie('token');
      console.log('FieldDetailsOverlay: Токен получен', { token: token ? 'есть' : 'нет' });
      
      const response = await getAnalysisList(token);
      console.log('FieldDetailsOverlay: Ответ от сервера на список анализов', { status: response.status });
      
      if (response.ok) {
        const data = await response.json();
        console.log('FieldDetailsOverlay: Данные списка анализов получены', { status: data.status, count: data.analyses?.length });
        
        if (data.status === 'success') {
          setAnalysesList(data.analyses || []);
          console.log('FieldDetailsOverlay: Список анализов обновлен', { count: data.analyses?.length });
        } else {
          console.error('FieldDetailsOverlay: Ошибка в статусе ответа списка анализов', data);
        }
      } else {
        console.error('FieldDetailsOverlay: Ошибка HTTP при загрузке списка анализов', response.status);
      }
    } catch (error) {
      console.error('FieldDetailsOverlay: Исключение при загрузке списка анализов:', error);
    }
  };

  const loadAnalysisById = async (analysisId) => {
    console.log('FieldDetailsOverlay: Загрузка анализа по ID', { analysisId });
    try {
      setLoading(true);
      const token = getCookie('token');
      const response = await getAnalysisById(analysisId, token);
      console.log('FieldDetailsOverlay: Ответ от сервера на загрузку анализа', { status: response.status });
      
      if (response.ok) {
        const data = await response.json();
        console.log('FieldDetailsOverlay: Данные анализа получены', { status: data.status, hasData: !!data.data });
        
        if (data.status === 'success') {
          setCurrentAnalysis(data.data);
          setSelectedAnalysisId(analysisId);
          setRecommendations(null); // Сбрасываем предыдущие рекомендации
          console.log('FieldDetailsOverlay: Анализ установлен как текущий', { analysisId });
          
          // Загружаем рекомендации для этого анализа
          loadRecommendations(analysisId);
        } else {
          console.error('FieldDetailsOverlay: Ошибка в статусе ответа анализа', data);
        }
      } else {
        console.error('FieldDetailsOverlay: Ошибка HTTP при загрузке анализа', response.status);
      }
    } catch (error) {
      console.error('FieldDetailsOverlay: Исключение при загрузке анализа:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadRecommendations = async (analysisId) => {
    console.log('FieldDetailsOverlay: Загрузка рекомендаций для анализа', { analysisId });
    try {
      setLoadingRecommendations(true);
      const token = getCookie('token');
      const response = await getAnalysisRecommendations(analysisId, token);
      console.log('FieldDetailsOverlay: Ответ от сервера на рекомендации', { status: response.status });
      
      if (response.ok) {
        const data = await response.json();
        console.log('FieldDetailsOverlay: Данные рекомендаций получены', { status: data.status, hasRecommendation: !!data.recommendation });
        
        if (data.status === 'success') {
          setRecommendations(data);
          console.log('FieldDetailsOverlay: Рекомендации установлены', { recommendation: data.recommendation });
        } else {
          console.error('FieldDetailsOverlay: Ошибка в статусе ответа рекомендаций', data);
        }
      } else {
        console.error('FieldDetailsOverlay: Ошибка HTTP при загрузке рекомендаций', response.status);
      }
    } catch (error) {
      console.error('FieldDetailsOverlay: Исключение при загрузке рекомендаций:', error);
    } finally {
      setLoadingRecommendations(false);
    }
  };

  const handleRunAnalysis = async () => {
    console.log('FieldDetailsOverlay: Запуск нового анализа для поля', { fieldId: field.id, fieldName: field.name });
    try {
      setLoading(true);
      const token = getCookie('token');
      
      // Получаем даты (сегодня и 30 дней назад)
      const endDate = new Date().toISOString().split('T')[0];
      const startDate = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
      
      console.log('FieldDetailsOverlay: Параметры анализа', { startDate, endDate, fieldType: field.area_of_interest.type });
      
      let response;
      
      if (field.area_of_interest.type === 'point_radius') {
        console.log('FieldDetailsOverlay: Анализ по точке с радиусом', field.area_of_interest);
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
        console.log('FieldDetailsOverlay: Анализ по полигону', { coordinatesCount: field.area_of_interest.coordinates?.length });
        response = await performAnalysis(
          token,
          startDate,
          endDate,
          {
            polygonCoords: field.area_of_interest.coordinates
          }
        );
      }
      
      console.log('FieldDetailsOverlay: Ответ от сервера на новый анализ', { status: response?.status });
      
      if (response.ok) {
        const result = await response.json();
        console.log('FieldDetailsOverlay: Результат нового анализа', { status: result.status, analysisId: result.analysis_id });
        
        if (result.status === 'success') {
          setCurrentAnalysis(result.data);
          setSelectedAnalysisId(result.analysis_id);
          setRecommendations(null); // Сбрасываем предыдущие рекомендации
          console.log('FieldDetailsOverlay: Новый анализ успешно выполнен', { analysisId: result.analysis_id });
          
          // Загружаем рекомендации для нового анализа
          loadRecommendations(result.analysis_id);
          
          // Обновляем список анализов
          await loadAnalysesList();
        } else {
          console.error('FieldDetailsOverlay: Ошибка в статусе нового анализа', result);
        }
      } else {
        console.error('FieldDetailsOverlay: Ошибка HTTP при выполнении анализа', response.status);
      }
    } catch (error) {
      console.error('FieldDetailsOverlay: Исключение при выполнении анализа:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) {
      console.log('FieldDetailsOverlay: Клик по оверлею, закрытие');
      handleClose();
    }
  };

  const handleClose = () => {
    console.log('FieldDetailsOverlay: Закрытие оверлея');
    setCurrentAnalysis(null);
    setSelectedAnalysisId(null);
    setRecommendations(null);
    onClose();
  };

  if (!isVisible) {
    console.log('FieldDetailsOverlay: Компонент не видим, возвращаем null');
    return null;
  }

  console.log('FieldDetailsOverlay: Рендер интерфейса', { 
    loading, 
    hasCurrentAnalysis: !!currentAnalysis, 
    analysesCount: analysesList.length,
    hasRecommendations: !!recommendations 
  });

  return (
    <div 
      className="fixed inset-0 bg-[var(--overlay-bg)] flex items-center justify-center z-50 p-4"
      onClick={handleOverlayClick}
    >
      <div className="bg-white rounded-3xl w-[90vw] h-[90vh] flex flex-col lg:flex-row overflow-hidden">
        {/* Левая секция - результаты анализа */}
        <div className="flex-1 p-6 overflow-y-auto">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-3xl lg:text-4xl font-bold text-[var(--neutral-dark-color)]">
              {field.name} - Результаты анализа
            </h2>
            <button
              onClick={handleClose}
              className="text-4xl text-gray-500 hover:text-gray-700 transition-colors cursor-pointer"
            >
              ×
            </button>
          </div>

          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-3xl">Загрузка...</div>
            </div>
          ) : currentAnalysis ? (
            <AnalysisResults 
              analysis={currentAnalysis} 
              recommendations={recommendations}
              loadingRecommendations={loadingRecommendations}
            />
          ) : (
            <div className="flex items-center justify-center h-64 text-3xl text-gray-500">
              Выберите анализ из списка или запустите новый
            </div>
          )}
        </div>
        
        {/* Правая секция - кнопка анализа и список анализов */}
        <div className="w-full lg:w-1/3 p-6 lg:p-8 border-l border-gray-200 flex flex-col">
          <div className="mb-6">
            <button
              onClick={handleRunAnalysis}
              disabled={loading}
              className="w-full bg-[var(--accent-color)] hover:bg-[var(--accent-light-color)] disabled:bg-gray-400 transition-colors rounded-full py-4 text-2xl font-semibold text-white cursor-pointer shadow-2xs"
            >
              {loading ? 'Анализ выполняется...' : 'Анализировать'}
            </button>
            <p className="text-xl text-gray-500 mt-3 text-center">
              Анализ за последние 30 дней
            </p>
          </div>

          <div className="flex-1 overflow-y-auto">
            <h3 className="text-2xl font-semibold mb-4 text-[var(--neutral-dark-color)]">
              История анализов
            </h3>
            {analysesList.length === 0 ? (
              <div className="text-gray-500 text-center py-4 text-xl">
                Нет выполненных анализов
              </div>
            ) : (
              <div className="space-y-4">
                {analysesList.map(analysis => (
                  <AnalysisListItem
                    key={analysis.analysis_id}
                    analysis={analysis}
                    isSelected={selectedAnalysisId === analysis.analysis_id}
                    onSelect={() => loadAnalysisById(analysis.analysis_id)}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// Компонент для отображения элемента списка анализов
function AnalysisListItem({ analysis, isSelected, onSelect }) {
  console.log('AnalysisListItem: Рендер элемента', { analysisId: analysis.analysis_id, isSelected });

  const formatDate = (timestamp) => {
    return new Date(timestamp * 1000).toLocaleDateString('ru-RU');
  };

  const getAreaType = (areaOfInterest) => {
    return areaOfInterest.type === 'point_radius' ? 'Точка' : 'Полигон';
  };

  return (
    <div
      className={`p-4 rounded-xl border-2 cursor-pointer transition-all ${
        isSelected 
          ? 'border-[var(--accent-color)] bg-gray-50' 
          : 'border-gray-200 hover:border-gray-300'
      }`}
      onClick={onSelect}
    >
      <div className="flex justify-between items-start mb-3">
        <span className="font-semibold text-xl">
          {formatDate(analysis.timestamp)}
        </span>
        <span className="text-lg text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
          {getAreaType(analysis.area_of_interest)}
        </span>
      </div>
      <div className="text-lg text-gray-600">
        <div>Снимков: {analysis.image_count}</div>
        {analysis.statistics_summary && (
          <div className="mt-2">
            NDVI: {analysis.statistics_summary.ndvi_mean?.toFixed(3) || 'N/A'}
          </div>
        )}
      </div>
    </div>
  );
}

// Компонент для отображения результатов анализа
function AnalysisResults({ analysis, recommendations, loadingRecommendations }) {
  console.log('AnalysisResults: Рендер результатов', { 
    analysisId: analysis.analysis_id,
    hasRecommendations: !!recommendations,
    loadingRecommendations 
  });

  return (
    <div className="space-y-6">
      {/* Основная информация */}
      <AnalysisHeader analysis={analysis} />
      
      {/* Рекомендации */}
      <RecommendationsSection 
        recommendations={recommendations} 
        loading={loadingRecommendations} 
      />
      
      {/* Статистика по каждому снимку */}
      {analysis.results_per_image && analysis.results_per_image.map((result, index) => (
        <ImageResults key={index} result={result} index={index} />
      ))}
    </div>
  );
}

// Компонент для отображения рекомендаций
function RecommendationsSection({ recommendations, loading }) {
  console.log('RecommendationsSection: Рендер рекомендаций', { hasRecommendations: !!recommendations, loading });

  if (loading) {
    return (
      <div className="bg-gray-50 p-5 rounded-xl border border-gray-200">
        <h4 className="font-semibold text-2xl mb-3 text-[var(--neutral-dark-color)]">AI Рекомендации</h4>
        <div className="text-xl text-gray-600">Загрузка рекомендаций...</div>
      </div>
    );
  }

  if (!recommendations) {
    return null;
  }

  return (
    <div className="bg-gray-50 p-5 rounded-xl border border-gray-200">
      <h4 className="font-semibold text-2xl mb-3 text-[var(--neutral-dark-color)]">AI Рекомендации</h4>
      <p className="text-xl text-gray-700 mb-4 whitespace-pre-wrap">{recommendations.recommendation}</p>
      
      {recommendations.average_indices && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <h5 className="font-medium text-xl text-[var(--neutral-dark-color)] mb-3">Средние показатели:</h5>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-lg">
            {Object.entries(recommendations.average_indices).map(([index, value]) => (
              <div key={index} className="text-gray-700">
                <span className="font-medium capitalize">{index}:</span>{' '}
                {typeof value === 'number' ? value.toFixed(4) : value}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// Компонент заголовка анализа
function AnalysisHeader({ analysis }) {
  console.log('AnalysisHeader: Рендер заголовка', { analysisId: analysis.analysis_id });

  const formatDateRange = (dateRange) => {
    return `${dateRange.start} - ${dateRange.end}`;
  };

  return (
    <div className="bg-gray-50 p-5 rounded-xl">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div>
          <h4 className="font-semibold text-2xl mb-3 text-[var(--neutral-dark-color)]">Информация об анализе</h4>
          <div className="space-y-2 text-xl">
            <div>ID: {analysis.analysis_id}</div>
            <div>Период: {formatDateRange(analysis.date_range)}</div>
            <div>Снимков: {analysis.image_count}</div>
          </div>
        </div>
        <div>
          <h4 className="font-semibold text-2xl mb-3 text-[var(--neutral-dark-color)]">Метаданные</h4>
          <div className="space-y-2 text-xl">
            <div>Источник: {analysis.metadata?.source || 'N/A'}</div>
            <div>Разрешение: {analysis.metadata?.resolution || 'N/A'}</div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Компонент для отображения результатов по одному снимку
function ImageResults({ result, index }) {
  console.log('ImageResults: Рендер результатов снимка', { index, date: result.date });

  const [selectedTab, setSelectedTab] = useState('images');

  return (
    <div className="border border-gray-200 rounded-xl overflow-hidden">
      <div className="bg-gray-100 px-5 py-4 border-b border-gray-200">
        <h4 className="font-semibold text-2xl">Снимок от {result.date}</h4>
        <p className="text-xl text-gray-600">
          Облачность: {result.cloud_coverage}%
        </p>
      </div>

      <div className="border-b border-gray-200">
        <div className="flex">
          <button
            className={`px-5 py-3 font-medium text-xl ${
              selectedTab === 'images' 
                ? 'text-[var(--accent-color)] border-b-2 border-[var(--accent-color)]' 
                : 'text-gray-500'
            }`}
            onClick={() => setSelectedTab('images')}
          >
            Изображения
          </button>
          <button
            className={`px-5 py-3 font-medium text-xl ${
              selectedTab === 'statistics' 
                ? 'text-[var(--accent-color)] border-b-2 border-[var(--accent-color)]' 
                : 'text-gray-500'
            }`}
            onClick={() => setSelectedTab('statistics')}
          >
            Статистика
          </button>
          <button
            className={`px-5 py-3 font-medium text-xl ${
              selectedTab === 'zoning' 
                ? 'text-[var(--accent-color)] border-b-2 border-[var(--accent-color)]' 
                : 'text-gray-500'
            }`}
            onClick={() => setSelectedTab('zoning')}
          >
            Зонирование
          </button>
        </div>
      </div>

      <div className="p-5">
        {selectedTab === 'images' && <AnalysisImages images={result.images} />}
        {selectedTab === 'statistics' && <AnalysisStatistics statistics={result.statistics} />}
        {selectedTab === 'zoning' && <AnalysisZoning zoning={result.zoning} />}
      </div>
    </div>
  );
}

// Компонент для отображения изображений
function AnalysisImages({ images }) {
  console.log('AnalysisImages: Рендер изображений', { imageTypes: images ? Object.keys(images) : 'none' });

  if (!images) return <div className="text-xl">Нет изображений</div>;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
      {Object.entries(images).map(([type, base64Data]) => (
        <div key={type} className="text-center">
          <div className="font-medium text-xl mb-3 capitalize">{type}</div>
          <img 
            src={`data:image/png;base64,${base64Data}`} 
            alt={type}
            className="w-full h-52 object-cover rounded-lg border border-gray-200"
          />
        </div>
      ))}
    </div>
  );
}

// Компонент для отображения статистики
function AnalysisStatistics({ statistics }) {
  console.log('AnalysisStatistics: Рендер статистики', { statisticTypes: statistics ? Object.keys(statistics) : 'none' });

  if (!statistics) return <div className="text-xl">Нет статистики</div>;

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full bg-white text-xl">
        <thead>
          <tr className="bg-gray-50">
            <th className="px-5 py-3 text-left">Индекс</th>
            <th className="px-5 py-3 text-left">Мин.</th>
            <th className="px-5 py-3 text-left">Макс.</th>
            <th className="px-5 py-3 text-left">Среднее</th>
            <th className="px-5 py-3 text-left">Ст. откл.</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(statistics).map(([index, data]) => (
            <tr key={index} className="border-b border-gray-200">
              <td className="px-5 py-3 font-medium capitalize">{index}</td>
              <td className="px-5 py-3">{data.min?.toFixed(4)}</td>
              <td className="px-5 py-3">{data.max?.toFixed(4)}</td>
              <td className="px-5 py-3">{data.mean?.toFixed(4)}</td>
              <td className="px-5 py-3">{data.std?.toFixed(4)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// Компонент для отображения зонирования
function AnalysisZoning({ zoning }) {
  console.log('AnalysisZoning: Рендер зонирования', { zoningTypes: zoning ? Object.keys(zoning) : 'none' });

  if (!zoning) return <div className="text-xl">Нет данных зонирования</div>;

  return (
    <div className="space-y-5">
      {Object.entries(zoning).map(([index, zones]) => (
        <div key={index} className="border border-gray-200 rounded-lg p-5">
          <h5 className="font-semibold text-xl mb-4 capitalize">{index} Зонирование</h5>
          <div className="space-y-3">
            {Object.entries(zones).map(([zone, percentage]) => (
              <div key={zone} className="flex items-center justify-between">
                <span className="capitalize text-xl">{zone} зона</span>
                <div className="flex items-center space-x-3">
                  <div className="w-40 bg-gray-200 rounded-full h-3">
                    <div 
                      className="bg-[var(--accent-color)] h-3 rounded-full" 
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                  <span className="text-xl font-medium w-16">
                    {percentage}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

export default FieldDetailsOverlay;