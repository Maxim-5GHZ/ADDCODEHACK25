import { Link, useNavigate } from "react-router-dom"
import { useState, useEffect } from "react"
import { getCookie, deleteCookie } from "../utils/cookies";
import { getUserProfile } from "../utils/fetch";
import { Footer } from "./Main";

function ProfileSidebar({ user, activeTab, setActiveTab }) {
  const tabs = [
    { id: "profile", label: "Профиль" },
    { id: "fields", label: "Список полей" },
    { id: "add", label: "Добавить поле" }
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

function FieldsTab({ setActiveTab }) {
  const fields = [
    
  ];

  return (
    <div className="container">
      <div className="text-3xl font-semibold mb-4">{fields.length === 0 ? "У вас ещё нет полей" : "Ваши поля:"}</div>
      <ul className="space-y-4">
        {fields.length !== 0 ? (fields.map((field) => (
          <li key={field.id} className="bg-[#f6f6f6] rounded-xl px-6 py-4 flex justify-between items-center">
            <span className="text-xl font-medium text-gray-900">{field.name}</span>
            <button className="text-[#009e4f] font-bold hover:underline text-lg">
              Подробнее
            </button>
          </li>
        ))) : (<div>
          <button onClick={() => setActiveTab("add")}
            className="bg-[var(--accent-color)] hover:bg-[var(--accent-light-color)] mt-6
            transition-[background-color] duration-100 cursor-pointer rounded-full text-3xl px-5 py-4 text-[var(--neutral-color)]">
            Добавить поле
          </button>
        </div>)}
      </ul>
    </div>
  );
}

function AddFieldTab() {
  return (
    <div>
      <form className="max-w-xl">
        <div className="mb-8">
          <label className="block text-2xl font-semibold mb-2" htmlFor="fieldName">
            Название поля
          </label>
          <input
            id="fieldName"
            type="text"
            className="w-full border rounded-xl px-6 py-4 text-xl focus:outline-none focus:ring-2 focus:ring-[#009e4f]"
            placeholder="Введите название"
          />
        </div>

        <div className="mb-8">
          <label className="block text-2xl font-semibold mb-2" htmlFor="fieldLocation">
            Местоположение
          </label>
          <input
            id="fieldLocation"
            type="text"
            className="w-full border rounded-xl px-6 py-4 text-xl focus:outline-none focus:ring-2 focus:ring-[#009e4f]"
            placeholder="Введите регион или координаты"
          />
        </div>

        <button type="sumbit"
            className="bg-[var(--accent-color)] hover:bg-[var(--accent-light-color)] mt-6
            transition-[background-color] duration-100 cursor-pointer rounded-full text-3xl px-5 py-4 text-[var(--neutral-color)]">
            Добавить поле
          </button>
      </form>
    </div>
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
      className="absolute text-2xl md:text-3xl self-start left-2 mx-16 my-8 hover:text-[var(--accent-dark-color)] transition-[color] duration-100"
    >
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
        return <FieldsTab setActiveTab={setActiveTab}/>;
      case "add":
        return <AddFieldTab />;
      default:
        return <ProfileTab user={user} />;
    }
  };

  return (
    <div className="flex flex-col min-h-screen">
    <BackButton />
    <div className="flex-1 flex justify-center bg-[var(--neutral-light-color)]">
      <div className="pt-24 pb-12 w-[80vw]">
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