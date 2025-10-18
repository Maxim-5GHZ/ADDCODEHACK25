import React from 'react';

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
    <div className="flex justify-between items-center mb-6 md:mb-8 lg:mb-10">
      <h1 className="text-2xl md:text-3xl lg:text-4xl xl:text-5xl font-bold text-[var(--neutral-dark-color)] tracking-tight">
        {getTitle()}
      </h1>
    </div>
  );
}

export default ProfileHeader;