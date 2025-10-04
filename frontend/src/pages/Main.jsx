import { useState, useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import Header from "../components/Header";
import { Card, HorizontalCard } from "../components/Card";
import logoSVG from "../assets/logo.svg"
import card1Image from "../assets/card1_image.jpg";
import card2Image from "../assets/card2_image.jpg";
import card3Image from "../assets/card3_image.jpg";
import card4Image from "../assets/card4_image.jpg";
import carousel1Image from "../assets/carousel_image1.jpg"
import carousel2Image from "../assets/carousel_image2.jpg"
import carousel3Image from "../assets/carousel_image3.jpg"
import carousel4Image from "../assets/carousel_image4.jpg"

function Hero() {
    return (
        <div id="main" className="bg-[url(assets/hero_image.jpg)] bg-cover h-240 bg-center relative">
            <div className="bg-[var(--hero-shadow)] h-full w-full pt-48 px-48 flex flex-col">
                <h1 className="text-8xl font-bold text-[var(--neutral-color)] tracking-tight">
                    Аналитика поля одним кликом
                </h1>
                <p className="text-3xl text-[var(--neutral-color)] mt-8 tracking-wider">
                    Просто укажите свой участок на карте — и наш искусственный<br />
                    интеллект на основе спутниковых снимков мгновенно проведёт<br />
                    диагностику. Получите готовый отчёт о состоянии почвы,<br />
                    растительности и потенциальных рисках для вашего урожая.
                </p>

                <div className="flex-grow flex items-end justify-center pb-48">
                    <Link
                        to="/registration"
                        className="bg-[var(--accent-color)] hover:bg-[var(--accent-light-color)]
                        transition-[background-color] duration-100 cursor-pointer rounded-full text-5xl px-8 py-6 text-[var(--neutral-color)] shadow-2xl"
                    >
                        Анализировать поле
                    </Link>
                </div>
            </div>
        </div>
    );
}

function AboutUs() {
    const card1Description = "Отметьте границы вашего участка на интерактивной карте. Это займёт не больше минуты. Никаких сложных карт или файлов — только точные координаты.";
    const card2Description = "Наша система через спутниковые API мгновенно загружает самый свежий снимок выбранной территории. Вам не нужно ждать или искать снимки вручную.";
    const card3Description = "Мощные алгоритмы искусственного интеллекта сканируют каждый пиксель изображения, выявляя проблемы и аномалии: стресс растительности, недостаток влаги, очаги болезней.";
    const card4Description = "Вы получаете структурированный отчёт с визуализацией проблемных зон и конкретными советами: где полить, чем обработать и на что обратить внимание.";

    return (
        <div id="about-us" className="bg-[var(--neutral-color)] w-full">
            <div className="lg:container mx-auto lg:w-[max(3/4vw, 1000px)] pt-16 pb-32">
                <div className="grid grid-cols-2 grid-rows-auto gap-y-16 gap-x-32">
                    <h2 className="text-8xl font-bold text-center col-span-2 self-center">О НАС</h2>
                    <p className="text-4xl text-start col-span-2 tracking-wider">
                        <strong>Мы создаём будущее сельского хозяйства,</strong> где технологии работают на результат
                        каждого фермера. Наша задача — дать вам не просто данные, а ясное понимание состояния ваших полей
                        и конкретные рекомендации для принятия решений. Всё, что для этого нужно, — всего несколько кликов.<br /><br />
                        <strong>Весь процесс от выбора поля до готового отчёта — прост и прозрачен</strong>
                    </p>

                    <div className="row-start-3 col-start-1">
                        <h2 className="text-9xl text-center text-[var(--neutral-dark-secondary-color)] mb-32 mt-16">
                            ШАГ 1 →
                        </h2>
                        <div className="flex justify-center">
                            <Card title="Получение снимков" description={card2Description} image={card2Image} />
                        </div>
                    </div>
                    <div className="row-start-3 col-start-2">
                        <div className="flex justify-center">
                            <Card title="Выбор участка" description={card1Description} image={card1Image} />
                        </div>
                        <h2 className="text-9xl text-center text-[var(--neutral-dark-secondary-color)] mb-32 mt-32">
                            ← ШАГ 2
                        </h2>
                    </div>
                    <div className="row-start-4 col-start-1">
                        <h2 className="text-9xl text-center text-[var(--neutral-dark-secondary-color)] mb-32 mt-16">
                            ШАГ 3 →
                        </h2>
                        <div className="flex justify-center">
                            <Card title="Подготовка отчета" description={card4Description} image={card4Image} />
                        </div>
                    </div>
                    <div className="row-start-4 col-start-2">
                        <div className="flex justify-center">
                            <Card title="Анализ снимков" description={card3Description} image={card3Image} />
                        </div>
                        <h2 className="text-9xl text-center text-[var(--neutral-dark-secondary-color)] mb-32 mt-32">
                            ← ШАГ 4
                        </h2>
                    </div>
                </div>
            </div>
        </div>
    );
}

function Advantages() {
    const carouselRef = useRef(null);
    
    let card1Description = "Диагностируйте угрозы на самой ранней стадии, когда их ещё не видно глазом. Спасайте урожай, а не констатируйте потери."
    let card2Description = "Никакого сложного оборудования и долгого обучения. Анализ поля — в несколько кликов, прямо в вашем браузере."
    let card3Description = "Ваши поля под наблюдением 24/7. Спутники работают даже когда вы спите."
    let card4Description = "Заменяйте догадки точными цифрами. Получайте конкретные рекомендации к действию: где полить, а где обработать от вредителей."

    const cards = [
        { title: "Предотвращение потерь урожая", description: card1Description, image: carousel1Image },
        { title: "Простота и доступность", description: card2Description, image: carousel2Image },
        { title: "Круглосуточный мониторинг", description: card3Description, image: carousel3Image },
        { title: "Принятие решений на основе данных", description: card4Description, image: carousel4Image }
    ];

    const duplicatedCards = [...cards, ...cards, ...cards];

    useEffect(() => {
        const carousel = carouselRef.current;
        if (!carousel) return;

        let animationId;
        const speed = 0.7;
        let position = 0;

        const animate = () => {
            position -= speed;
            
            if (position <= -carousel.scrollWidth / 3) {
                position = 0;
            }
            
            carousel.style.transform = `translateX(${position}px)`;
            animationId = requestAnimationFrame(animate);
        };

        const startAnimation = setTimeout(() => {
            animationId = requestAnimationFrame(animate);
        }, 100);

        return () => {
            clearTimeout(startAnimation);
            cancelAnimationFrame(animationId);
        };
    }, []);

    return (
        <div className="bg-[var(--neutral-secondary-color)] overflow-hidden">
            <div id="advantages" className="bg-[var(--neutral-secondary-color)] pt-16">
                <h3 className="text-8xl text-[var(--neutral-dark-color)] font-bold text-center">
                    ПРЕИМУЩЕСТВА
                </h3>
            </div>
            
            <div className="relative bg-[var(--neutral-secondary-color)] py-20 overflow-hidden">
                <div 
                    ref={carouselRef}
                    className="flex space-x-32 transition-transform duration-0"
                    style={{ willChange: 'transform' }}
                >
                    {duplicatedCards.map((card, index) => (
                        <div key={index} className="flex-shrink-0">
                            <HorizontalCard 
                                title={card.title} 
                                description={card.description} 
                                image={card.image} 
                            />
                        </div>
                    ))}
                </div>
                
                <div className="absolute left-0 top-0 bottom-0 w-32 bg-gradient-to-r from-[var(--neutral-secondary-color)] to-transparent z-10"></div>
                <div className="absolute right-0 top-0 bottom-0 w-32 bg-gradient-to-l from-[var(--neutral-secondary-color)] to-transparent z-10"></div>
            </div>

            <div className="flex flex-col justify-center items-center bg-[var(--neutral-secondary-color)] pt-16 pb-32">
                <Link
                    to="/registration"
                    className="bg-[var(--accent-color)] hover:bg-[var(--accent-light-color)]
                    transition-[background-color] duration-100 cursor-pointer rounded-full text-5xl px-8 py-6 text-[var(--neutral-color)] shadow-2xl"
                >
                    Анализировать поле
                </Link>
            </div>
        </div>
    );
}


function Footer() {
    return (
        <footer className="bg-[var(--neutral-dark-color)] pt-16 pb-8">
            <div className="max-w-7xl mx-auto px-8">
                <div className="flex flex-col md:flex-row justify-between items-center gap-8 pb-8 border-b border-[var(--neutral-color)]">
                    <div className="flex flex-col items-start">
                        <div className="flex items-center gap-4 mb-4">
                            <img src={logoSVG} alt="FieldScan" className="h-16 w-16" />
                            <span className="text-4xl font-bold text-[var(--accent-color)] tracking-tight">FieldScan</span>
                        </div>
                        <span className="text-xl text-gray-500 font-medium mb-2">2025 © Все права защищены</span>
                        <span className="text-lg text-gray-400">Создано для будущего агроаналитики</span>
                    </div>
                    <nav className="flex flex-col md:flex-row gap-6 items-center">
                        <a href="#main" className="text-2xl text-[var(--accent-color)] hover:text-[var(--accent-light-color)] transition-[color]">
                            Главная
                        </a>
                        <a href="#about-us" className="text-2xl text-[var(--accent-color)] hover:text-[var(--accent-light-color)] transition-[color]">
                            О нас
                        </a>
                        <a href="#advantages" className="text-2xl text-[var(--accent-color)] hover:text-[var(--accent-light-color)] transition-[color]">
                            Преимущества
                        </a>
                    </nav>
                </div>
                <div className="text-center text-gray-400 text-lg pt-6">
                    FieldScan — ваш помощник в цифровом сельском хозяйстве
                </div>
            </div>
        </footer>
    );
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

        return () => window.removeEventListener("scroll", handleScroll);
    }, []);

    return (
        <>
            <Header isTransparent={isHeaderTransparent} />
            <Hero />
            <AboutUs />
            <Advantages />
            <Footer />
        </>
    );
}

export default Main;
