import { Link } from "react-router-dom"
import { useState } from "react"

export default function Profile() {
  const user = {
    name: "Никита Кузин",
    email: "example.email@domen.com"
  }

  // State для активной вкладки
  const [activeTab, setActiveTab] = useState("profile");

  return (
    <>
      <Link to="/" className="absolute text-2xl md:text-3xl self-start left-2 mx-16 my-8 hover:text-[var(--accent-dark-color)] transition-[color] duration-100">
        ← На главную
      </Link>

    <div className="bg-[var(--neutral-light-color)]">

      {/* Обёртка страницы: на весь экран */}
      <div className="bg-[var(--neutral-light-color)] min-h-screen pt-24 pb-12 container mx-auto">
        {/* Контейнер теперь растянут на всю ширину, с внутренними отступами */}
        <div className="flex w-full space-x-16 px-8">
          {/* Sidebar (левое меню) — без теней, остаётся фиксированной ширины */}
          <aside className="rounded-2xl w-80 flex flex-col items-center py-8 px-6 mt-2 h-fit sticky top-24">
            <div className="flex flex-col items-center mb-8">
              <div className="w-20 h-20 rounded-full bg-gradient-to-tr from-[var(--accent-dark-color)] to-[var(--accent-light-color)] flex items-center justify-center mb-3">
                {/* SVG аватар */}
                <svg width="40" height="40" fill="none" stroke="#fff" strokeWidth="2" viewBox="0 0 24 24">
                  <circle cx="12" cy="8" r="4"/>
                  <path d="M4 20c0-4 8-4 8-4s8 0 8 4"/>
                </svg>
              </div>
              <span className="text-3xl lg:text-4xl font-bold text-[var(--accent-color)]">{user.name}</span>
            </div>

            <nav className="flex flex-col gap-3 w-full">
              <button
                className={`text-2xl font-semibold rounded-xl py-2 px-4 transition-all text-left w-full text-start ${
                  activeTab === "profile"
                    ? "bg-[var(--neutral-color)] text-[var(--accent-color)]"
                    : "text-gray-500 hover:text-[var(--accent-light-color)] hover:bg-[var(--neutral-color)]"
                }`}
                onClick={() => setActiveTab("profile")}
              >
                Профиль
              </button>

              <button
                className={`text-2xl font-semibold rounded-xl py-2 px-4 transition-all text-left w-full text-start ${
                  activeTab === "fields"
                    ? "bg-[var(--neutral-color)] text-[var(--accent-color)]"
                    : "text-gray-500 hover:text-[var(--accent-light-color)] hover:bg-[var(--neutral-color)]"
                }`}
                onClick={() => setActiveTab("fields")}
              >
                Список полей
              </button>

              <button
                className={`text-2xl font-semibold rounded-xl py-2 px-4 transition-all text-left w-full text-start ${
                  activeTab === "add"
                    ? "bg-[var(--neutral-color)] text-[var(--accent-color)]"
                    : "text-gray-500 hover:text-[var(--accent-light-color)] hover:bg-[var(--neutral-color)]"
                }`}
                onClick={() => setActiveTab("add")}
              >
                Добавить поле
              </button>
            </nav>
          </aside>

          {/* Main profile info — растянутая область, без теней */}
          <main className="flex-1 rounded-2xl p-12 mt-2">
            <div className="flex justify-between items-center mb-10">
              <h1 className="text-5xl font-bold text-[#009e4f] tracking-tight">
                {activeTab === "profile"
                  ? "Мой профиль"
                  : activeTab === "fields"
                  ? "Список полей"
                  : "Добавить поле"}
              </h1>
            </div>

            {/* Контент вкладок */}
            {activeTab === "profile" && (
              <>
                <div className="grid grid-cols-2 gap-y-8 gap-x-16 mb-14">
                  <div className="text-2xl text-gray-500">Имя</div>
                  <div className="text-2xl font-semibold text-gray-900">{user.name}</div>
                  <div className="text-2xl text-gray-500">Email</div>
                  <div className="text-2xl font-semibold text-gray-900">{user.email}</div>
                </div>

                <div className="flex gap-6">
                  <button className="bg-[#009e4f] hover:bg-[#00c97b] text-white rounded-xl px-10 py-4 text-2xl font-bold transition-colors">
                    Редактировать профиль
                  </button>
                  <button className="bg-white border-2 border-[#009e4f] text-[#009e4f] rounded-xl px-10 py-4 text-2xl font-bold hover:bg-[#f6f6f6] transition-colors">
                    Сменить пароль
                  </button>
                </div>
              </>
            )}

            {activeTab === "fields" && (
              <div className="container">
                <div className="text-3xl font-semibold mb-4">Ваши поля:</div>
                <ul className="space-y-4">
                  <li className="bg-[#f6f6f6] rounded-xl px-6 py-4 flex justify-between items-center">
                    <span className="text-xl font-medium text-gray-900">Поле №1 — Воронежская область</span>
                    <button className="text-[#009e4f] font-bold hover:underline text-lg">Подробнее</button>
                  </li>
                  <li className="bg-[#f6f6f6] rounded-xl px-6 py-4 flex justify-between items-center">
                    <span className="text-xl font-medium text-gray-900">Поле №2 — Краснодарский край</span>
                    <button className="text-[#009e4f] font-bold hover:underline text-lg">Подробнее</button>
                  </li>
                </ul>
              </div>
            )}

            {activeTab === "add" && (
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

                  <button
                    type="submit"
                    className="bg-[#009e4f] hover:bg-[#00c97b] text-white rounded-xl px-10 py-4 text-2xl font-bold transition-colors"
                  >
                    Добавить поле
                  </button>
                </form>
              </div>
            )}
          </main>
        </div>
      </div>
    </div>
    </>
  )
}
