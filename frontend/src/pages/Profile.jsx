import { useNavigate } from "react-router-dom"
import { useState, useEffect } from "react"
import { getCookie, deleteCookie } from "../utils/cookies";
import { getUserProfile } from "../utils/fetch";
import { Footer } from "./Main";

// Импорт компонентов
import LoadingSpinner from "../components/Common/LoadingSpinner";
import BackButton from "../components/Common/BackButton";
import ProfileSidebar from "../components/Profile/ProfileSidebar";
import ProfileHeader from "../components/Profile/ProfileHeader";
import ProfileTab from "../components/Profile/ProfileTab";
import FieldsTab from "../components/Profile/FieldsTab";

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