import { useState } from 'react'
import './App.css'

function Header() {
  return (
    <header className="bg-[var(--neutral-color)] shadow-sm">
      <div className="px-32">
        <div className="flex items-center justify-between h-20">
          <div className="flex-shrink-0">
            <a href="index.html" className="text-6xl text-[var(--neutral-dark-color)] cousine-regular">Field Scan</a>
          </div>

          <nav className="hidden md:flex space-x-16">
            <a href="#" className="text-3xl text-[var(--neutral-dark-color)] hover:text-[var(--accent-dark-color)] transition-colors duration-100">
              Главная
            </a>
            <a href="#" className="text-3xl text-[var(--neutral-dark-color)] hover:text-[var(--accent-dark-color)] transition-colors duration-100">
              О нас
            </a>
            <a href="#" className="text-3xl text-[var(--neutral-dark-color)] hover:text-[var(--accent-dark-color)] transition-colors duration-100">
              Преимущества
            </a>
          </nav>

          <div className="flex items-center space-x-16">
            <button className="text-3xl text-[var(--neutral-dark-color)] hover:text-[var(--accent-dark-color)] transition-colors duration-100 cursor-pointer">
              Войти
            </button>
            <button className="text-3xl text-[var(--neutral-dark-color)] hover:text-[var(--accent-dark-color)] transition-colors duration-100 cursor-pointer">
              Зарегистрироваться
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}

function Hero() {
  return (
    <>
      <div className='bg-gray-400 min-h-100'>
        <h1>Аналитика поля одним кликом</h1>
        <p>Просто укажите свой участок на карте — и наш искусственный интеллект на 
          основе спутниковых снимков мгновенно проведёт диагностику. Получите 
          готовый отчёт о состоянии почвы, растительности и потенциальных 
          рисках для вашего урожая.</p>
          <button className='primary-button'>Анализировать поле</button>
      </div>
    </>
  )
}

function AboutUs() {
  return (
    <>
      <div className='bg-gray-500 min-h-100'>

        </div>
    </>
  )
}

function Advantages() {
  return (
    <>
      <div className='bg-gray-800 min-h-100'>

        </div>
    </>
  )
}

function Footer() {
  return (
    <>
      <div className='bg-gray-800 min-h-100'>

        </div>
    </>
  )
}

function App() {
  return (
    <>
      <Header />
      <Hero />
      <AboutUs />
      <Advantages />
      <Footer />
    </>
  )
}

export default App
