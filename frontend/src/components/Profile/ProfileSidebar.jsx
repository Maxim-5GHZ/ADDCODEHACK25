import React from 'react';

function ProfileSidebar({ user, activeTab, setActiveTab }) {
  const tabs = [
    { id: "profile", label: "Профиль" },
    { id: "fields", label: "Список полей" },
    { id: "analyses", label: "Анализы" },
  ];

  return (
    <aside className="rounded-xl md:rounded-2xl w-full lg:w-80 flex flex-col items-center py-4 md:py-6 lg:py-8 px-4 md:px-6 mt-0 lg:mt-2 h-fit lg:sticky lg:top-24">
      <div className="flex flex-col items-center mb-4 md:mb-6 lg:mb-8">
        <div className="w-12 h-12 md:w-16 md:h-16 lg:w-20 lg:h-20 rounded-full bg-[var(--neutral-dark-color)] flex items-center justify-center mb-2 md:mb-3">
          <svg width="24" height="24" md:width="32" md:height="32" lg:width="40" lg:height="40" fill="none" stroke="#fff" strokeWidth="2" viewBox="0 0 24 24">
            <circle cx="12" cy="8" r="4"/>
            <path d="M4 20c0-4 8-4 8-4s8 0 8 4"/>
          </svg>
        </div>
        <span className="text-xl md:text-2xl lg:text-3xl xl:text-4xl font-semibold text-center text-[var(--neutral-dark-color)] break-words max-w-full">
          {user.name}
        </span>
      </div>

      <nav className="flex flex-row lg:flex-col gap-2 md:gap-3 w-full overflow-x-auto lg:overflow-visible pb-2 lg:pb-0">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`text-base md:text-xl lg:text-2xl rounded-lg md:rounded-xl py-2 px-3 md:py-2 md:px-4 transition-all whitespace-nowrap flex-shrink-0 lg:w-full text-start cursor-pointer ${
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