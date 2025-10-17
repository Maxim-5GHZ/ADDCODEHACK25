import React from 'react';

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
          className="bg-white hover:bg-[var(--neutral-light-color)] border-2 border-[var(--accent-color)]
          transition-[background-color] duration-100 cursor-pointer rounded-full text-3xl px-5 py-4 text-[var(--accent-color)]">
          Сменить пароль
        </button>
      </div>
    </>
  );
}

export default ProfileTab;
