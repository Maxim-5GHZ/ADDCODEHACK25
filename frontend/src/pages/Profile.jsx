import { Link, useNavigate } from "react-router-dom"
import { useState, useEffect, useRef } from "react"
import { getCookie, deleteCookie } from "../utils/cookies";
import { getUserProfile } from "../utils/fetch";
import { Footer } from "./Main";

// Импорты OpenLayers
import 'ol/ol.css';
import Map from 'ol/Map';
import View from 'ol/View';
import TileLayer from 'ol/layer/Tile';
import OSM from 'ol/source/OSM';
import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
import Draw from 'ol/interaction/Draw';
import Modify from 'ol/interaction/Modify';
import Select from 'ol/interaction/Select';
import { Circle as CircleStyle, Fill, Stroke, Style } from 'ol/style';
import { getArea, getLength } from 'ol/sphere';
import { LineString, Polygon, Circle } from 'ol/geom';
import { unByKey } from 'ol/Observable';
import Overlay from 'ol/Overlay';
import { fromCircle } from 'ol/geom/Polygon';
import { getDistance } from 'ol/sphere';
import Point from 'ol/geom/Point';

// Новый компонент для выбора типа поля
function FieldTypeSelector({ fieldType, setFieldType }) {
  return (
    <div className="mb-6">
      <label className="block text-2xl font-semibold mb-4">Тип поля</label>
      <div className="flex gap-4">
        <button
          type="button"
          className={`px-6 py-3 rounded-xl text-xl transition-all ${
            fieldType === 'polygon'
              ? 'bg-[var(--accent-color)] text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
          onClick={() => setFieldType('polygon')}
        >
          Полигон (3-5 вершин)
        </button>
        <button
          type="button"
          className={`px-6 py-3 rounded-xl text-xl transition-all ${
            fieldType === 'point'
              ? 'bg-[var(--accent-color)] text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
          onClick={() => setFieldType('point')}
        >
          Точка с радиусом
        </button>
      </div>
    </div>
  );
}

// Компонент для формы ввода данных поля
function FieldForm({ fieldType, fieldName, setFieldName, radius, setRadius, area, perimeter }) {
  return (
    <div className="space-y-6">
      <div>
        <label className="block text-2xl font-semibold mb-2" htmlFor="fieldName">
          Название поля
        </label>
        <input
          id="fieldName"
          type="text"
          value={fieldName}
          onChange={(e) => setFieldName(e.target.value)}
          className="w-full border rounded-xl px-6 py-4 text-xl focus:outline-none focus:ring-2 focus:ring-[#009e4f]"
          placeholder="Введите название поля"
        />
      </div>

      {area && (
        <div className="bg-green-50 p-4 rounded-xl border border-green-200">
          <p className="text-lg font-semibold text-green-800">
            Площадь: {area}
          </p>
          {perimeter && (
            <p className="text-lg font-semibold text-green-800 mt-2">
              Периметр: {perimeter}
            </p>
          )}
        </div>
      )}

      {fieldType === 'point' && (
        <div>
          <label className="block text-2xl font-semibold mb-2" htmlFor="radius">
            Радиус (метры)
          </label>
          <input
            id="radius"
            type="number"
            value={radius}
            onChange={(e) => setRadius(parseInt(e.target.value) || 100)}
            className="w-full border rounded-xl px-6 py-4 text-xl focus:outline-none focus:ring-2 focus:ring-[#009e4f]"
            placeholder="Введите радиус"
            min="1"
          />
        </div>
      )}

      {fieldType === 'polygon' && (
        <div className="text-lg text-gray-600 bg-yellow-50 p-4 rounded-xl">
          <p>ℹ️ Выберите на карте от 3 до 5 точек для создания полигона</p>
          <p className="text-sm mt-2">• Кликните на карте, чтобы добавить вершины</p>
          <p className="text-sm">• Двойной клик или нажмите Enter для завершения</p>
          <p className="text-sm">• Перетащите точки для изменения формы</p>
        </div>
      )}
    </div>
  );
}

// Компонент карты с OpenLayers
function OpenLayersMap({ fieldType, onGeometryChange, radius }) {
  const mapRef = useRef(null);
  const mapInstance = useRef(null);
  const drawInteraction = useRef(null);
  const modifyInteraction = useRef(null);
  const vectorSource = useRef(new VectorSource());
  const [area, setArea] = useState(null);
  const [perimeter, setPerimeter] = useState(null);

  // Стили для разных типов фигур
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

    // Создание карты
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
        center: [4188099.476, 7505781.418], // Центр России
        zoom: 4
      })
    });

    // Добавляем взаимодействие для модификации
    const modify = new Modify({
      source: vectorSource.current
    });
    map.addInteraction(modify);
    modifyInteraction.current = modify;

    // Обработчик изменения геометрии
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

  // Функция для обновления измерений
  const updateMeasurements = (feature) => {
    const geometry = feature.getGeometry();
    
    if (geometry.getType() === 'Polygon') {
      const areaValue = getArea(geometry);
      const areaHectares = (areaValue / 10000).toFixed(2);
      setArea(`${areaHectares} га`);
      
      // Вычисляем периметр
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

    // Удаляем предыдущее взаимодействие рисования
    if (drawInteraction.current) {
      mapInstance.current.removeInteraction(drawInteraction.current);
      drawInteraction.current = null;
    }

    if (fieldType === 'polygon') {
      // Создаем взаимодействие для рисования полигонов
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
      // Создаем взаимодействие для рисования точек
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
        
        // Создаем круг вокруг точки
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

  // Обновляем радиус круга при изменении
  useEffect(() => {
    if (fieldType === 'point' && radius) {
      // Находим все круги и обновляем их радиус
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

// Основной компонент overlay
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
      
      // Вычисляем периметр
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
      const vertexCount = coordinates[0].length - 1; // -1 потому что полигон замкнутый
      
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
      onClose();
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
        {/* Левая часть - карта */}
        <div className="flex-1 p-6 min-h-[300px] lg:min-h-auto">
          <OpenLayersMap 
            fieldType={fieldType}
            onGeometryChange={handleGeometryChange}
            radius={radius}
          />
        </div>
        
        {/* Правая часть - форма */}
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

// Обновленный компонент FieldsTab
function FieldsTab() {
  const [showAddFieldOverlay, setShowAddFieldOverlay] = useState(false);
  const fields = [
    {id: 1, name: "first-field"},
    {id: 2, name: "second-field"},
    {id: 3, name: "third-field"},
    {id: 4, name: "fourth-field"}
  ];

  const handleAddFieldSubmit = (fieldData) => {
    console.log("Данные нового поля:", fieldData);
    // Здесь будет логика сохранения поля
    setShowAddFieldOverlay(false);
  };

  return (
    <>
      <div className="container">
        <div className="text-3xl font-semibold mb-4">
          {fields.length === 0 ? "У вас ещё нет полей" : "Ваши поля:"}
        </div>
        <ul className="space-y-4 max-h-[20vh] overflow-y-auto">
          {fields.map(field => (
            <li key={field.id} className="bg-[#f6f6f6] rounded-xl px-6 py-4 flex justify-between items-center">
              <span className="text-xl font-medium text-gray-900">{field.name}</span>
              <button className="text-[#009e4f] font-bold hover:underline text-lg">
                Подробнее
              </button>
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
    </>
  );
}

// Остальные компоненты остаются без изменений...
function ProfileSidebar({ user, activeTab, setActiveTab }) {
  const tabs = [
    { id: "profile", label: "Профиль" },
    { id: "fields", label: "Список полей" },
  ];

  return (
    <aside className="rounded-2xl w-80 flex flex-col items-center py-8 px-6 mt-2 h-fit sticky top-24">
      <div className="flex flex-col items-center mb-8">
        <div className="w-20 h-20 rounded-full bg-[var(--neutral-dark-color)] flex items-center justify-center mb-3">
          <svg width="40" height="40" fill="none" stroke="#fff" strokeWidth="2" viewBox="0 0 24 24">
            <circle cx="12" cy="8" r="4"/>
            <path d="M4 20c0-4 8-4 8-4s8 0 8 4"/>
          </svg>
        </div>
        <span className="text-3xl lg:text-4xl font-semibold text-center text-[var(--netral-dark-color)]">
          {user.name}
        </span>
      </div>

      <nav className="flex flex-col gap-3 w-full">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`text-2xl rounded-xl py-2 px-4 transition-all w-full text-start cursor-pointer ${
              activeTab === tab.id
                ? "bg-[var(--neutral-color)] text-[var(--accent-color)]"
                : "text-gray-500 hover:text-[var(--accent-light-color)] hover:bg-gray-100"
            }`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </nav>
    </aside>
  );
}

function ProfileHeader({ activeTab }) {
  const getTitle = () => {
    switch (activeTab) {
      case "profile": return "Мой профиль";
      case "fields": return "Список полей";
      case "add": return "Добавить поле";
      default: return "Мой профиль";
    }
  };

  return (
    <div className="flex justify-between items-center mb-10">
      <h1 className="text-5xl font-bold text-[var(--neutral-dark-color)] tracking-tight">
        {getTitle()}
      </h1>
    </div>
  );
}

function ProfileTab({ user }) {
  return (
    <>
      <div className="grid grid-cols-2 gap-y-8 gap-x-16 mb-14">
        <div className="text-2xl text-gray-500">Имя</div>
        <div className="text-2xl font-semibold text-[var(--neutral-dark-color)]">{user.name}</div>
        <div className="text-2xl text-gray-500">Email</div>
        <div className="text-2xl font-semibold text-[var(--neutral-dark-color)]">{user.email}</div>
      </div>

      <div className="flex gap-6">
        <button
          className="bg-[var(--accent-color)] hover:bg-[var(--accent-light-color)]
          transition-[background-color] duration-100 cursor-pointer rounded-full text-3xl px-5 py-4 text-[var(--neutral-color)]">
          Редактировать профиль
        </button>
        <button
          className="bg-[var(--neutral-light-color)] hover:bg-[var(--neutral-color)] border-2 border-[var(--accent-color)]
          transition-[background-color] duration-100 cursor-pointer rounded-full text-3xl px-5 py-4 text-[var(--accent-color)]">
          Сменить пароль
        </button>
      </div>
    </>
  );
}

function LoadingSpinner() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-2xl">Загрузка...</div>
    </div>
  );
}

function BackButton() {
  return (
    <Link 
      to="/" 
      className="absolute text-2xl md:text-3xl self-start left-2 mx-16 my-8 hover:text-[var(--accent-dark-color)] transition-[color] duration-100">
      ← На главную
    </Link>
  );
}

export default function Profile() {
  const [activeTab, setActiveTab] = useState("profile");
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      deleteCookie("token");
      navigate("/login");
    }
    catch (error){
      console.log(`Error logging out: ${error}`);
      navigate("/login");
    }
  }

  useEffect(() => {
    const fetchUserProfile = async () => {
      const token = getCookie('token');
      console.log(`Token: ${token}`)
      if (!token) {
        navigate('/login');
        return;
      }

      try {
        const response = await getUserProfile(token);
        
        const contentType = response.headers.get('content-type');
        
        if (contentType && contentType.includes('application/json')) {
          const data = await response.json();

          if (data.status === 'success') {
            setUser({
              name: `${data.user.first_name} ${data.user.last_name}`,
              email: data.user.login
            });
          } else {
            console.error('Ошибка от сервера:', data);
            navigate('/login');
          }
        } else {
          const text = await response.text();
          console.error('Сервер вернул HTML вместо JSON:', text.substring(0, 200));
          navigate('/login');
        }
      } catch (error) {
        console.error('Ошибка при получении профиля:', error);
        navigate('/login');
      } finally {
        setLoading(false);
      }
    };

    fetchUserProfile();
  }, [navigate]);

  useEffect(() => {
    console.log('API_BASE должен быть настроен в fetch.js');
  }, []);

  if (loading) {
    return <LoadingSpinner />;
  }

  if (!user) {
    return null;
  }

  const renderActiveTab = () => {
    switch (activeTab) {
      case "profile":
        return <ProfileTab user={user} />;
      case "fields":
        return <FieldsTab />;
      default:
        return <ProfileTab user={user} />;
    }
  };

  return (
    <div className="flex flex-col min-h-screen">
      <BackButton />
      <div className="flex-1 flex justify-center bg-[var(--neutral-light-color)] py-24">
        <div className="pt-24 pb-12 w-[80vw] bg-white rounded-[4vw]">
          <div className="flex w-full space-x-16 px-8 h-full">
            <ProfileSidebar 
              user={user} 
              activeTab={activeTab} 
              setActiveTab={setActiveTab} 
            />

            <main className="flex-1 rounded-2xl p-12 mt-2">
              <ProfileHeader activeTab={activeTab} />
              {renderActiveTab()}
            </main>
          </div>
        </div>
      </div>
      <Footer showNavigation={false} logoutFunction={handleLogout} />
    </div>
  );
}