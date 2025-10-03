import { useState, useEffect } from "react"
import { Link } from "react-router-dom"
import Header from "../components/Header"
import Card from "../components/Card"
import card1Image from "../assets/card1_image.jpg"
import card2Image from "../assets/card2_image.jpg"
import card3Image from "../assets/card3_image.jpg"
import card4Image from "../assets/card4_image.jpg"

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
                <Link to="/registration" className='bg-[var(--accent-color)] hover:bg-[var(--accent-light-color)]
                transition-[background-color] duration-100 cursor-pointer rounded-full text-5xl px-8 py-6 text-[var(--neutral-color)] shadow-2xl'>
                    Анализировать поле
                </Link>
            </div>
        </div>
        </div>
    </>
    )
}

function AboutUs() {
    const card1Description = "Отметьте границы вашего участка на интерактивной карте. Это займёт не больше минуты. Никаких сложных карт или файлов — только точные координаты."
    const card2Description = "Наша система через спутниковые API мгновенно загружает самый свежий снимок выбранной территории. Вам не нужно ждать или искать снимки вручную."
    const card3Description = "Мощные алгоритмы искусственного интеллекта сканируют каждый пиксель изображения, выявляя проблемы и аномалии: стресс растительности, недостаток влаги, очаги болезней."
    const card4Description = "Вы получаете структурированный отчёт с визуализацией проблемных зон и конкретными советами: где полить, чем обработать и на что обратить внимание."

    return (
    <>
        <div id="about-us" className='bg-[var(--neutral-color)]'>
        <div className='md:container mx-auto w-full lg:w-[max(2/3vw, 800px)] pt-16 pb-32'>
            <div className='grid grid-cols-2 grid-rows-auto gap-y-16 gap-x-32'>
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
        <div id="advantages" className='bg-[var(--neutral-dark-color)] min-h-100'>
        <div className='flex justify-center items-center h-100'>
            <h2 className='text-8xl font-bold text-[var(--neutral-color)]'>
            ПРЕИМУЩЕСТВА
            </h2>
        </div>
        </div>
    </>
    )
}

function Footer() {
    return (
    <>
        <div className='bg-[var(--neutral-dark-secondary-color)]'>
        <div className='grid grid-cols-2 justify-center'>
            <div className='flex flex-col'>
            <h3 className='text-9xl text-[var(--neutral-dark-color)] font-bold cousine-bold'>
                Field<br />
                Scan<br />
                2025<br />
            </h3>
            <h6 className='text-3xl font-bold'>
                Field Scan 2025©. Все права защищены
            </h6>
            </div>
            <div className='flex flex-col text-center items-center my-auto'>
            <a href="#main" className="text-4xl font-bold transition-colors duration-100">
                Главная
            </a>
            <a href="#main" className="text-4xl font-bold transition-colors duration-100">
                О нас
            </a>
            <a href="#main" className="text-4xl font-bold transition-colors duration-100">
                Преимущества
            </a>
            <a href="#main" className="mt-4 text-4xl font-bold transition-colors duration-100">
                Вход
            </a>
            <a href="#main" className="text-4xl font-bold transition-colors duration-100">
                Регистрация
            </a>
            <a href="#main" className="text-4xl font-bold transition-colors duration-100">
                Анализ поля
            </a>
            </div>
        </div>
        </div>
    </>
    )
}

function Main() {
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

export default Main