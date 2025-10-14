import React from 'react';

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

export default ProfileSidebar;
