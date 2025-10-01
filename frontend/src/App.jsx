import { useState } from 'react'
import './App.css'

function Header() {
  return (
    <header className="bg-[var(--neutral-color)] shadow-2xl fixed w-dvw z-1">
      <div className="px-32">
        <div className="flex items-center justify-between h-20">
          <div className="flex-shrink-0">
            <a href="index.html" className="text-6xl text-[var(--neutral-dark-color)] cousine-regular">Field Scan</a>
          </div>

          <nav className="hidden md:flex gap-x-16">
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

          <div className="flex items-center gap-x-16">
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
      <div className='bg-[url(assets/hero_image.jpg)] bg-cover h-240 bg-center relative'>
        <div className='bg-[var(--hero-shadow)] h-full w-full pt-48 px-48 flex flex-col'>
          <h1 className='text-8xl font-bold text-[var(--neutral-color)] tracking-tight'>Аналитика поля одним кликом</h1>
          <p className='text-3xl text-[var(--neutral-color)] mt-8 tracking-wider'>
            Просто укажите свой участок на карте — и наш искусственный<br/>
            интеллект на основе спутниковых снимков мгновенно проведёт<br/>
            диагностику. Получите готовый отчёт о состоянии почвы,<br /> 
            растительности и потенциальных рисках для вашего урожая.
          </p>
          
          <div className='flex-grow flex items-end justify-center pb-48'>
            <button className='bg-[var(--accent-color)] hover:bg-[var(--accent-light-color)] 
            transition-[background-color] duration-100 cursor-pointer rounded-[10rem] text-5xl px-8 py-6 text-[var(--neutral-color)] shadow-2xl'>
              Анализировать поле
            </button>
          </div>
        </div>
      </div>
    </>
  )
}

function AboutUs() {
  return (
    <>
      <div className='bg-[var(--neutral-color)] min-h-100'>

        </div>
    </>
  )
}

function Advantages() {
  return (
    <>
      <div className='bg-[var(--neutral-dark-color)] min-h-100'>

        </div>
    </>
  )
}

function Footer() {
  return (
    <>
      <div className='bg-[var(--neutral-dark-secondary-color)] min-h-100'>

        </div>
    </>
  )
}

function App() {
  return (
    <>
      <Header/>
      <Hero />
      <AboutUs />
      <Advantages />
      <Footer />
    </>
  )
}

export default App
