import React from 'react';

function ProfileTab({ user }) {
  return (
    <>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-y-4 gap-x-8 md:gap-y-6 lg:gap-y-8 lg:gap-x-16 mb-8 md:mb-10 lg:mb-14">
        <div className="text-lg md:text-xl lg:text-2xl text-gray-500">Имя</div>
        <div className="text-lg md:text-xl lg:text-2xl font-semibold text-[var(--neutral-dark-color)] break-words">{user.name}</div>
        <div className="text-lg md:text-xl lg:text-2xl text-gray-500">Email</div>
        <div className="text-lg md:text-xl lg:text-2xl font-semibold text-[var(--neutral-dark-color)] break-words">{user.email}</div>
      </div>

      {/* Кнопки для редактирования профиля и смены пароля (на сервере нет эндпоинта, поэтому кнопки убраны) */}
      {/* 
      <div className="flex gap-6">
        <button
          className="bg-[var(--accent-color)] hover:bg-[var(--accent-light-color)]
          transition-[background-color] duration-100 cursor-pointer rounded-full text-3xl px-5 py-4 text-[var(--neutral-color)]">
          Редактировать профиль
        </button>
        <button
          className="bg-white hover:bg-[var(--neutral-light-color)] border-2 border-[var(--accent-color)]
          transition-[background-color] duration-100 cursor-pointer rounded-full text-3xl px-5 py-4 text-[var(--accent-color)]">
          Сменить пароль
        </button>
      </div>
      */}
    </>
  );
}

export default ProfileTab;
