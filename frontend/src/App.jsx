import { useState, useEffect } from 'react'
import Card from './components/Card'
import card1Image from './assets/card1_image.jpg'
import card2Image from './assets/card2_image.jpg'
import card3Image from './assets/card3_image.jpg'
import card4Image from './assets/card4_image.jpg'
import './App.css'

function Header({ isTransparent }) {
  let navButtonsStyle = isTransparent ? "text-[var(--neutral-color)] hover:text-[var(--accent-light-color)]" : "text-[var(--neutral-dark-color)] hover:text-[var(--accent-dark-color)]"
  return (
    <header id='header' className={`shadow-md fixed w-dvw z-1 ${isTransparent ? "bg-[var(--header-blur)] backdrop-blur-xs" : "bg-[var(--neutral-color)]" }`}>
      <div className="px-32">
        <div className="flex items-center justify-between h-20">
          <div className="flex-shrink-0">
            <a href="index.html" className={`text-6xl cousine-regular ${isTransparent ? "text-[var(--neutral-color)]" : "text-[var(--neutral-dark-color)]"}`}>Field Scan</a>
          </div>

          <nav className="hidden md:flex gap-x-16">
            <a href="#main" className={`${navButtonsStyle} text-3xl transition-colors duration-100`}>
              Главная
            </a>
            <a href="#about-us" className={`${navButtonsStyle} text-3xl transition-colors duration-100"`}>
              О нас
            </a>
            <a href="#" className={`${navButtonsStyle} text-3xl transition-colors duration-100"`}>
              Преимущества
            </a>
          </nav>

          <div className="flex items-center gap-x-16">
            <a href='' className={`${navButtonsStyle} text-3xl transition-colors duration-100"`}>
              Войти
            </a>
            <a href='' className={`${navButtonsStyle} text-3xl transition-colors duration-100"`}>
              Зарегистрироваться
            </a>
          </div>
        </div>
      </div>
    </header>
  );
}

function Hero() {
  return (
    <>
      <div id="main" className='bg-[url(assets/hero_image.jpg)] bg-cover h-240 bg-center relative'>
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
            transition-[background-color] duration-100 cursor-pointer rounded-full text-5xl px-8 py-6 text-[var(--neutral-color)] shadow-2xl'>
              Анализировать поле
            </button>
          </div>
        </div>
      </div>
    </>
  )
}

function AboutUs() {
  let card1Description = "Отметьте границы вашего участка на интерактивной карте. Это займёт не больше минуты. Никаких сложных карт или файлов — только точные координаты."
  let card2Description = "Наша система через спутниковые API мгновенно загружает самый свежий снимок выбранной территории. Вам не нужно ждать или искать снимки вручную."
  let card3Description = "Мощные алгоритмы искусственного интеллекта сканируют каждый пиксель изображения, выявляя проблемы и аномалии: стресс растительности, недостаток влаги, очаги болезней."
  let card4Description = "Вы получаете структурированный отчёт с визуализацией проблемных зон и конкретными советами: где полить, чем обработать и на что обратить внимание."

  return (
    <>
      <div id="about-us" className='bg-[var(--neutral-color)] h-[200rem]'>
        <div className='container mx-auto max-w-2/3 pt-16 pb-32'>
          <div className='grid grid-cols-2 grid-rows-auto gap-y-16'>
            <h2 className='text-8xl font-bold text-center col-span-2 self-center'>
              О НАС
            </h2>
            <p className='text-4xl text-start col-span-2 tracking-wider'>
              <strong>Мы создаём будущее сельского хозяйства,</strong> где технологии работают на результат 
              каждого фермера. Наша задача — дать вам не просто данные, а ясное понимание состояния ваших полей и конкретные рекомендации 
              для принятия решений. Всё, что для этого нужно, — всего несколько кликов.<br /><br />
              <strong>Весь процесс от выбора поля до готового отчёта — прост и прозрачен</strong>
            </p>
            <div className='row-start-3 col-start-1'>
              <h2 className='text-9xl text-center text-[var(--neutral-dark-secondary-color)] mb-32 mt-16'>
                ШАГ 1 →
              </h2>
              <div className='flex justify-center'>
                <Card title='Получение снимков' description={card2Description} image={card2Image}/>
              </div>
            </div>
            <div className='row-start-3 col-start-2'>
              <div className='flex justify-center'>
                <Card title='Выбор участка' description={card1Description} image={card1Image}/>
              </div>
              <h2 className='text-9xl text-center text-[var(--neutral-dark-secondary-color)] mb-32 mt-32'>
                ← ШАГ 2
              </h2>
            </div>
            <div className='row-start-4 col-start-1'>
              <h2 className='text-9xl text-center text-[var(--neutral-dark-secondary-color)] mb-32 mt-16'>
                ШАГ 3 →
              </h2>
              <div className='flex justify-center'>
                <Card title='Подготовка отчета' description={card4Description} image={card4Image}/>
              </div>
            </div>
            <div className='row-start-4 col-start-2'>
              <div className='flex justify-center'>
                <Card title='Анализ снимков' description={card3Description} image={card3Image}/>
              </div>
              <h2 className='text-9xl text-center text-[var(--neutral-dark-secondary-color)] mb-32 mt-32'>
                ← ШАГ 4
              </h2>
            </div>
          </div>
        </div>
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
  const [isHeaderTransparent, setIsHeaderTransparent] = useState(true);
  useEffect(() => {
    const handleScroll = () => {
      const heroSection = document.getElementById("main");
      if (!heroSection) return;
      const headerHeight = document.getElementById("header").offsetHeight;
      const heroBottom = heroSection.offsetTop + heroSection.offsetHeight;
      const currentScroll = window.scrollY + headerHeight;

      setIsHeaderTransparent(currentScroll < heroBottom);
    };
    handleScroll();
    window.addEventListener("scroll", handleScroll);

    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <>
      <Header isTransparent={isHeaderTransparent}/>
      <Hero />
      <AboutUs />
      <Advantages />
      <Footer />
    </>
  )
}

export default App
