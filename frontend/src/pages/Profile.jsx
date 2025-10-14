import { Link, useNavigate } from "react-router-dom"
import { useState, useEffect } from "react"
import { getCookie, deleteCookie } from "../utils/cookies";
import { getUserProfile } from "../utils/fetch";
import { Footer } from "./Main";

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
function FieldForm({ fieldType, fieldName, setFieldName, radius, setRadius }) {
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

      {fieldType === 'point' && (
        <div>
          <label className="block text-2xl font-semibold mb-2" htmlFor="radius">
            Радиус (метры)
          </label>
          <input
            id="radius"
            type="number"
            value={radius}
            onChange={(e) => setRadius(e.target.value)}
            className="w-full border rounded-xl px-6 py-4 text-xl focus:outline-none focus:ring-2 focus:ring-[#009e4f]"
            placeholder="Введите радиус"
            min="1"
          />
        </div>
      )}

      {fieldType === 'polygon' && (
        <div className="text-lg text-gray-600 bg-yellow-50 p-4 rounded-xl">
          <p>ℹ️ Выберите на карте от 3 до 5 точек для создания полигона</p>
        </div>
      )}
    </div>
  );
}

// Компонент карты (заглушка - нужно заменить на реальную Google Maps)
function MapComponent({ fieldType }) {
  return (
    <div className="flex-1 bg-gray-200 rounded-xl flex items-center justify-center">
      <div className="text-center p-8">
        <div className="text-3xl mb-4">🗺️</div>
        <h3 className="text-2xl font-semibold mb-4">Карта для выбора участка</h3>
        <p className="text-lg text-gray-600 mb-2">
          {fieldType === 'polygon' 
            ? 'Режим: выбор полигона (3-5 точек)'
            : 'Режим: выбор точки и радиуса'
          }
        </p>
        <p className="text-sm text-gray-500">
          Здесь будет интегрирована Google Maps API
        </p>
      </div>
    </div>
  );
}

// Основной компонент overlay
function AddFieldOverlay({ isVisible, onClose, onSubmit }) {
  const [fieldType, setFieldType] = useState('polygon');
  const [fieldName, setFieldName] = useState('');
  const [radius, setRadius] = useState(100);

  const handleSubmit = (e) => {
    e.preventDefault();
    // Здесь будет логика отправки данных
    onSubmit({
      type: fieldType,
      name: fieldName,
      radius: fieldType === 'point' ? radius : undefined
    });
  };

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  if (!isVisible) return null;

  return (
    <div 
      className="fixed inset-0 bg-[var(--overlay-bg)] flex items-center justify-center z-50 p-4"
      onClick={handleOverlayClick}
    >
      <div className="bg-white rounded-3xl w-full max-w-6xl h-[80vh] flex overflow-hidden">
        {/* Левая часть - карта */}
        <div className="flex-1 p-6">
          <MapComponent fieldType={fieldType} />
        </div>
        
        {/* Правая часть - форма */}
        <div className="w-1/3 p-8 flex flex-col">
          <div className="flex justify-between items-center mb-8">
            <h2 className="text-3xl font-bold text-[var(--neutral-dark-color)]">
              Добавить поле
            </h2>
            <button
              onClick={onClose}
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
            />
            
            <div className="mt-auto pt-8 flex gap-4">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 bg-gray-200 hover:bg-gray-300 transition-colors rounded-xl py-4 text-xl font-semibold text-gray-700"
              >
                Отмена
              </button>
              <button
                type="submit"
                className="flex-1 bg-[var(--accent-color)] hover:bg-[var(--accent-light-color)] transition-colors rounded-xl py-4 text-xl font-semibold text-white"
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