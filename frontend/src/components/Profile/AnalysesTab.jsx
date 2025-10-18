import React, { useState, useEffect } from 'react';
import { getCookie } from '../../utils/cookies';
import { getAnalysisList, getAnalysisById, getAnalysisRecommendations } from '../../utils/fetch';
import MapOverlay from './MapOverlay';

function AnalysesTab() {
  const [analysesList, setAnalysesList] = useState([]);
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadingDetails, setLoadingDetails] = useState(false);
  const [error, setError] = useState('');

  console.log('AnalysesTab: Рендер компонента');

  // Загрузка списка анализов
  const loadAnalyses = async () => {
    console.log('AnalysesTab: Начало загрузки списка анализов');
    try {
      setLoading(true);
      const token = getCookie('token');
      console.log('AnalysesTab: Токен получен', { token: token ? 'есть' : 'нет' });
      
      const response = await getAnalysisList(token);
      console.log('AnalysesTab: Ответ от сервера на список анализов', { status: response.status });
      
      if (response.ok) {
        const data = await response.json();
        console.log('AnalysesTab: Данные списка анализов получены', { status: data.status, count: data.analyses?.length });
        
        if (data.status === 'success') {
          // Сортируем анализы по дате (новые сверху)
          const sortedAnalyses = (data.analyses || []).sort((a, b) => b.timestamp - a.timestamp);
          setAnalysesList(sortedAnalyses);
          console.log('AnalysesTab: Список анализов обновлен', { count: sortedAnalyses.length });
        } else {
          setError('Ошибка при загрузке списка анализов');
          console.error('AnalysesTab: Ошибка в статусе ответа списка анализов', data);
        }
      } else {
        setError('Ошибка соединения с сервером');
        console.error('AnalysesTab: Ошибка HTTP при загрузке списка анализов', response.status);
      }
    } catch (error) {
      setError('Ошибка при загрузке анализов');
      console.error('AnalysesTab: Исключение при загрузке списка анализов:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAnalyses();
  }, []);

  const handleSelectAnalysis = async (analysis) => {
    console.log('AnalysesTab: Выбор анализа', { analysisId: analysis.analysis_id });
    try {
      setLoadingDetails(true);
      const token = getCookie('token');
      const response = await getAnalysisById(analysis.analysis_id, token);
      console.log('AnalysesTab: Ответ от сервера на загрузку анализа', { status: response.status });
      
      if (response.ok) {
        const data = await response.json();
        console.log('AnalysesTab: Данные анализа получены', { status: data.status, hasData: !!data.data });
        
        if (data.status === 'success') {
          setSelectedAnalysis(data.data);
          setRecommendations(null);
          console.log('AnalysesTab: Анализ установлен как выбранный', { analysisId: analysis.analysis_id });
          
          // Загружаем рекомендации для этого анализа
          loadRecommendations(analysis.analysis_id);
        } else {
          console.error('AnalysesTab: Ошибка в статусе ответа анализа', data);
        }
      } else {
        console.error('AnalysesTab: Ошибка HTTP при загрузке анализа', response.status);
      }
    } catch (error) {
      console.error('AnalysesTab: Исключение при загрузке анализа:', error);
    } finally {
      setLoadingDetails(false);
    }
  };

  const loadRecommendations = async (analysisId) => {
    console.log('AnalysesTab: Загрузка рекомендаций для анализа', { analysisId });
    try {
      const token = getCookie('token');
      const response = await getAnalysisRecommendations(analysisId, token);
      console.log('AnalysesTab: Ответ от сервера на рекомендации', { status: response.status });
      
      if (response.ok) {
        const data = await response.json();
        console.log('AnalysesTab: Данные рекомендаций получены', { status: data.status, hasRecommendation: !!data.recommendation });
        
        if (data.status === 'success') {
          setRecommendations(data);
          console.log('AnalysesTab: Рекомендации установлены', { recommendation: data.recommendation });
        } else {
          console.error('AnalysesTab: Ошибка в статусе ответа рекомендаций', data);
        }
      } else {
        console.error('AnalysesTab: Ошибка HTTP при загрузке рекомендаций', response.status);
      }
    } catch (error) {
      console.error('AnalysesTab: Исключение при загрузке рекомендаций:', error);
    }
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp * 1000).toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getAreaDescription = (areaOfInterest) => {
    if (areaOfInterest.type === 'point_radius') {
      return `Точка (${areaOfInterest.lon.toFixed(4)}, ${areaOfInterest.lat.toFixed(4)}) с радиусом ${areaOfInterest.radius_km} км`;
    } else if (areaOfInterest.type === 'polygon') {
      return `Полигон с ${areaOfInterest.coordinates.length} точками`;
    }
    return 'Неизвестный тип области';
  };

  if (loading) {
    return (
      <div className="container">
        <div className="text-xl md:text-2xl lg:text-3xl font-semibold mb-4">Загрузка анализов...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container">
        <div className="text-xl md:text-2xl lg:text-3xl font-semibold mb-4 text-red-500">{error}</div>
        <button 
          onClick={loadAnalyses}
          className="bg-[var(--accent-color)] hover:bg-[var(--accent-light-color)] mt-4 md:mt-6
          transition-[background-color] duration-100 cursor-pointer rounded-full text-lg md:text-xl lg:text-2xl xl:text-3xl px-4 md:px-5 py-3 md:py-4 text-white"
        >
          Попробовать снова
        </button>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="text-xl md:text-2xl lg:text-3xl font-semibold mb-4">
        {analysesList.length === 0 ? "У вас ещё нет анализов" : "История анализов:"}
      </div>

      <div className="flex flex-col lg:flex-row gap-4 md:gap-6">
        {/* Список анализов */}
        <div className="lg:w-1/3">
          <div className="space-y-3 md:space-y-4 max-h-[50vh] md:max-h-[60vh] overflow-y-auto">
            {analysesList.map(analysis => (
              <div
                key={analysis.analysis_id}
                className={`p-3 md:p-4 rounded-lg md:rounded-xl border-2 cursor-pointer transition-all ${
                  selectedAnalysis?.analysis_id === analysis.analysis_id
                    ? 'border-[var(--accent-color)] bg-gray-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => handleSelectAnalysis(analysis)}
              >
                <div className="flex flex-col sm:flex-row justify-between items-start mb-2 md:mb-3">
                  <span className="font-semibold text-lg md:text-xl mb-1 sm:mb-0">
                    {formatDate(analysis.timestamp)}
                  </span>
                  <span className="text-base md:text-lg text-gray-500 bg-gray-100 px-2 md:px-3 py-1 rounded-full">
                    {analysis.image_count} снимков
                  </span>
                </div>
                <div className="text-base md:text-lg text-gray-600">
                  <div className="mb-1 md:mb-2">{getAreaDescription(analysis.area_of_interest)}</div>
                  <div>Период: {analysis.date_range.start} - {analysis.date_range.end}</div>
                  {analysis.statistics_summary && (
                    <div className="mt-1 md:mt-2">
                      NDVI: {analysis.statistics_summary.ndvi_mean?.toFixed(3) || 'N/A'}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Детали анализа */}
        <div className="lg:w-2/3">
          {loadingDetails ? (
            <div className="flex items-center justify-center h-40 md:h-64">
              <div className="text-xl md:text-2xl lg:text-3xl">Загрузка деталей анализа...</div>
            </div>
          ) : selectedAnalysis ? (
            <AnalysisDetails 
              analysis={selectedAnalysis} 
              recommendations={recommendations}
            />
          ) : (
            <div className="flex items-center justify-center h-40 md:h-64 text-xl md:text-2xl lg:text-3xl text-gray-500 border-2 border-dashed border-gray-300 rounded-lg md:rounded-xl p-4 text-center">
              Выберите анализ для просмотра деталей
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function AnalysisDetails({ analysis, recommendations }) {
  const [selectedMapType, setSelectedMapType] = useState('ndvi_overlay_image');
  const [selectedImageData, setSelectedImageData] = useState(null);
  const [selectedImageBounds, setSelectedImageBounds] = useState(null);

  // Определяем доступные типы карт на основе данных
  const availableMapTypes = [];
  if (analysis.results_per_image && analysis.results_per_image.length > 0) {
    const firstResult = analysis.results_per_image[0];
    if (firstResult.ndvi_overlay_image) availableMapTypes.push('ndvi_overlay_image');
    if (firstResult.problem_zones_image) availableMapTypes.push('problem_zones_image');
  }

  // Обновляем выбранные данные карты при изменении типа или анализа
  useEffect(() => {
    if (analysis.results_per_image && analysis.results_per_image.length > 0) {
      const firstResult = analysis.results_per_image[0];
      setSelectedImageData(firstResult[selectedMapType]);
      setSelectedImageBounds(firstResult.bounds);
    }
  }, [analysis, selectedMapType]);

  return (
    <div className="space-y-4 md:space-y-6">
      {/* Основная информация */}
      <div className="bg-gray-50 p-4 md:p-5 rounded-lg md:rounded-xl">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-5">
          <div>
            <h4 className="font-semibold text-xl md:text-2xl mb-2 md:mb-3 text-[var(--neutral-dark-color)]">Информация об анализе</h4>
            <div className="space-y-1 md:space-y-2 text-lg md:text-xl">
              <div>ID: {analysis.analysis_id}</div>
              <div>Период: {analysis.date_range.start} - {analysis.date_range.end}</div>
              <div>Снимков: {analysis.image_count}</div>
            </div>
          </div>
          <div>
            <h4 className="font-semibold text-xl md:text-2xl mb-2 md:mb-3 text-[var(--neutral-dark-color)]">Метаданные</h4>
            <div className="space-y-1 md:space-y-2 text-lg md:text-xl">
              <div>Источник: {analysis.metadata?.source || 'N/A'}</div>
              <div>Разрешение: {analysis.metadata?.resolution || 'N/A'}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Рекомендации */}
      {recommendations && (
        <div className="bg-gray-50 p-4 md:p-5 rounded-lg md:rounded-xl border border-gray-200">
          <h4 className="font-semibold text-xl md:text-2xl mb-2 md:mb-3 text-[var(--neutral-dark-color)]">AI Рекомендации</h4>
          <p className="text-lg md:text-xl text-gray-700 mb-3 md:mb-4 whitespace-pre-wrap">{recommendations.recommendation}</p>
          
          {recommendations.average_indices && (
            <div className="mt-3 md:mt-4 pt-3 md:pt-4 border-t border-gray-200">
              <h5 className="font-medium text-lg md:text-xl text-[var(--neutral-dark-color)] mb-2 md:mb-3">Средние показатели:</h5>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2 md:gap-3 text-base md:text-lg">
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
      )}

      {/* Карта с результатами анализа */}
      {availableMapTypes.length > 0 && selectedImageData && (
        <div className="bg-gray-50 p-4 md:p-5 rounded-lg md:rounded-xl border border-gray-200">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-3 md:mb-4">
            <h4 className="font-semibold text-xl md:text-2xl mb-2 sm:mb-0 text-[var(--neutral-dark-color)]">Визуализация анализа</h4>
            <div className="flex flex-wrap gap-2">
              {availableMapTypes.includes('ndvi_overlay_image') && (
                <button
                  onClick={() => setSelectedMapType('ndvi_overlay_image')}
                  className={`px-3 md:px-4 py-1 md:py-2 rounded-full text-base md:text-lg font-medium transition-colors ${
                    selectedMapType === 'ndvi_overlay_image'
                      ? 'bg-[var(--accent-color)] text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300 cursor-pointer'
                  }`}
                >
                  NDVI карта
                </button>
              )}
              {availableMapTypes.includes('problem_zones_image') && (
                <button
                  onClick={() => setSelectedMapType('problem_zones_image')}
                  className={`px-3 md:px-4 py-1 md:py-2 rounded-full text-base md:text-lg font-medium transition-colors ${
                    selectedMapType === 'problem_zones_image'
                      ? 'bg-[var(--accent-color)] text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300 cursor-pointer'
                  }`}
                >
                  Проблемные зоны
                </button>
              )}
            </div>
          </div>
          
          <div className="h-64 md:h-80 lg:h-96 xl:h-[500px] rounded-lg overflow-hidden border border-gray-300">
            <MapOverlay
              imageData={selectedImageData}
              bounds={selectedImageBounds}
              imageType={selectedMapType}
            />
          </div>
          
          <div className="mt-2 md:mt-3 text-base md:text-lg text-gray-600">
            {selectedMapType === 'ndvi_overlay_image' 
              ? 'Карта NDVI показывает распределение вегетационного индекса по полю'
              : 'Карта проблемных зон выделяет области с потенциальными проблемами'}
          </div>
        </div>
      )}

      {/* Статистика по каждому снимку */}
      {analysis.results_per_image && analysis.results_per_image.map((result, index) => (
        <ImageResults key={index} result={result} index={index} />
      ))}
    </div>
  );
}

// Компонент для отображения результатов по одному снимку
function ImageResults({ result, index }) {
  const [selectedTab, setSelectedTab] = useState('images');

  return (
    <div className="border border-gray-200 rounded-lg md:rounded-xl overflow-hidden">
      <div className="bg-gray-100 px-3 md:px-4 lg:px-5 py-3 md:py-4 border-b border-gray-200">
        <h4 className="font-semibold text-lg md:text-xl lg:text-2xl">Снимок от {result.date}</h4>
        <p className="text-base md:text-lg lg:text-xl text-gray-600">
          Облачность: {result.cloud_coverage}%
        </p>
      </div>

      <div className="border-b border-gray-200">
        <div className="flex overflow-x-auto">
          <button
            className={`px-3 md:px-4 lg:px-5 py-2 md:py-3 font-medium text-base md:text-lg lg:text-xl whitespace-nowrap ${
              selectedTab === 'images' 
                ? 'text-[var(--accent-color)] border-b-2 border-[var(--accent-color)]' 
                : 'text-gray-500'
            }`}
            onClick={() => setSelectedTab('images')}
          >
            Изображения
          </button>
          <button
            className={`px-3 md:px-4 lg:px-5 py-2 md:py-3 font-medium text-base md:text-lg lg:text-xl whitespace-nowrap ${
              selectedTab === 'statistics' 
                ? 'text-[var(--accent-color)] border-b-2 border-[var(--accent-color)]' 
                : 'text-gray-500'
            }`}
            onClick={() => setSelectedTab('statistics')}
          >
            Статистика
          </button>
          <button
            className={`px-3 md:px-4 lg:px-5 py-2 md:py-3 font-medium text-base md:text-lg lg:text-xl whitespace-nowrap ${
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

      <div className="p-3 md:p-4 lg:p-5">
        {selectedTab === 'images' && <AnalysisImages images={result.images} />}
        {selectedTab === 'statistics' && <AnalysisStatistics statistics={result.statistics} />}
        {selectedTab === 'zoning' && <AnalysisZoning zoning={result.zoning} />}
      </div>
    </div>
  );
}

// Компонент для отображения изображений
function AnalysisImages({ images }) {
  if (!images) return <div className="text-lg md:text-xl">Нет изображений</div>;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 md:gap-4 lg:gap-5">
      {Object.entries(images).map(([type, base64Data]) => (
        <div key={type} className="text-center">
          <div className="font-medium text-lg md:text-xl mb-2 md:mb-3 capitalize">{type}</div>
          <img 
            src={`data:image/png;base64,${base64Data}`} 
            alt={type}
            className="w-full h-40 md:h-52 object-cover rounded-lg border border-gray-200"
          />
        </div>
      ))}
    </div>
  );
}

// Компонент для отображения статистики
function AnalysisStatistics({ statistics }) {
  if (!statistics) return <div className="text-lg md:text-xl">Нет статистики</div>;

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full bg-white text-base md:text-lg lg:text-xl">
        <thead>
          <tr className="bg-gray-50">
            <th className="px-3 md:px-4 lg:px-5 py-2 md:py-3 text-left">Индекс</th>
            <th className="px-3 md:px-4 lg:px-5 py-2 md:py-3 text-left">Мин.</th>
            <th className="px-3 md:px-4 lg:px-5 py-2 md:py-3 text-left">Макс.</th>
            <th className="px-3 md:px-4 lg:px-5 py-2 md:py-3 text-left">Среднее</th>
            <th className="px-3 md:px-4 lg:px-5 py-2 md:py-3 text-left">Ст. откл.</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(statistics).map(([index, data]) => (
            <tr key={index} className="border-b border-gray-200">
              <td className="px-3 md:px-4 lg:px-5 py-2 md:py-3 font-medium capitalize">{index}</td>
              <td className="px-3 md:px-4 lg:px-5 py-2 md:py-3">{data.min?.toFixed(4)}</td>
              <td className="px-3 md:px-4 lg:px-5 py-2 md:py-3">{data.max?.toFixed(4)}</td>
              <td className="px-3 md:px-4 lg:px-5 py-2 md:py-3">{data.mean?.toFixed(4)}</td>
              <td className="px-3 md:px-4 lg:px-5 py-2 md:py-3">{data.std?.toFixed(4)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// Компонент для отображения зонирования
function AnalysisZoning({ zoning }) {
  if (!zoning) return <div className="text-lg md:text-xl">Нет данных зонирования</div>;

  return (
    <div className="space-y-3 md:space-y-4 lg:space-y-5">
      {Object.entries(zoning).map(([index, zones]) => (
        <div key={index} className="border border-gray-200 rounded-lg p-3 md:p-4 lg:p-5">
          <h5 className="font-semibold text-lg md:text-xl mb-3 md:mb-4 capitalize">{index} Зонирование</h5>
          <div className="space-y-2 md:space-y-3">
            {Object.entries(zones).map(([zone, percentage]) => (
              <div key={zone} className="flex items-center justify-between">
                <span className="capitalize text-base md:text-lg lg:text-xl">{zone} зона</span>
                <div className="flex items-center space-x-2 md:space-x-3">
                  <div className="w-24 md:w-32 lg:w-40 bg-gray-200 rounded-full h-2 md:h-3">
                    <div 
                      className="bg-[var(--accent-color)] h-2 md:h-3 rounded-full" 
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                  <span className="text-base md:text-lg lg:text-xl font-medium w-10 md:w-12 lg:w-16 text-right">
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

export default AnalysesTab;