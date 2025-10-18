import { useNavigate } from "react-router-dom"
import { useState, useEffect } from "react"
import { getCookie, deleteCookie, isValidToken } from "../utils/cookies";
import { getUserProfile } from "../utils/fetch";
import { Footer } from "./Main";

// Импорт компонентов
import LoadingSpinner from "../components/Common/LoadingSpinner";
import BackButton from "../components/Common/BackButton";
import ProfileSidebar from "../components/Profile/ProfileSidebar";
import ProfileHeader from "../components/Profile/ProfileHeader";
import ProfileTab from "../components/Profile/ProfileTab";
import FieldsTab from "../components/Profile/FieldsTab";
import AnalysesTab from "../components/Profile/AnalysesTab";

export default function Profile() {
  const [activeTab, setActiveTab] = useState("profile");
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
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
      
      // Проверяем наличие и базовую валидность токена
      if (!token || !isValidToken(token)) {
        deleteCookie("token");
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
            setError("");
          } else {
            console.error('Ошибка от сервера:', data);
            setError("Ошибка загрузки профиля");
            deleteCookie('token');
            navigate('/login');
          }
        } else {
          const text = await response.text();
          console.error('Сервер вернул HTML вместо JSON:', text.substring(0, 200));
          setError("Неверный формат ответа от сервера");
          deleteCookie('token');
          navigate('/login');
        }
      } catch (error) {
        console.error('Ошибка при получении профиля:', error);
        setError("Ошибка соединения с сервером");
        deleteCookie('token');
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

  if (error && !user) {
    return (
      <div className="flex flex-col min-h-screen justify-center items-center p-4">
        <div className="text-red-500 text-lg md:text-xl mb-4 text-center">{error}</div>
        <button 
          onClick={() => navigate('/login')}
          className="bg-[var(--accent-color)] text-white px-4 py-2 rounded text-base md:text-lg"
        >
          Вернуться к входу
        </button>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  const renderActiveTab = () => {
    switch (activeTab) {
      case "profile":
        return <ProfileTab user={user} />;
      case "fields":
        return <FieldsTab setActiveTab={setActiveTab} />;
      case "analyses":
        return <AnalysesTab />;
      default:
        return <ProfileTab user={user} />;
    }
  };

  return (
    <div className="flex flex-col min-h-screen">
      <BackButton />
      <div className="flex-1 flex justify-center bg-[var(--neutral-light-color)] py-4 md:py-8 lg:py-24">
        <div className="pt-16 md:pt-20 lg:pt-24 pb-8 md:pb-12 w-[95vw] md:w-[90vw] lg:w-[80vw] bg-white rounded-2xl md:rounded-3xl lg:rounded-[4vw]">
          <div className="flex flex-col lg:flex-row w-full lg:space-x-8 xl:space-x-16 space-y-6 lg:space-y-0 px-4 md:px-6 lg:px-8 h-full">
            <ProfileSidebar 
              user={user} 
              activeTab={activeTab} 
              setActiveTab={setActiveTab} 
            />

            <main className="flex-1 rounded-xl md:rounded-2xl p-4 md:p-6 lg:p-8 xl:p-12 mt-0 lg:mt-2">
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