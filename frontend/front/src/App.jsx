import { useState } from 'react'
import './App.css'

function Header() {
  return (
    <>
      <div className='header-style'>
        <div className='flex flex-row justify-between flex-wrap mx-30'>
          <h1>Field Scan</h1>
          <nav className='flex '>
            <a>Главная</a>
            <a>О нас</a>
            <a>Преимещства</a>
          </nav>
          <nav>
            <a>Войти</a>
            <a>Зарегистрироватбся</a>
          </nav>
        </div>
      </div>
    </>
  )
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
