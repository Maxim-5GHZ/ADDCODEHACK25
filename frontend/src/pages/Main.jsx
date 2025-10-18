import { useState, useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import Header from "../components/Header";
import { Card, HorizontalCard } from "../components/Card";
import { getCookie } from "../utils/cookies"
import logoSVG from "../assets/logo.svg"
import card1Image from "../assets/card1_image.webp";
import card2Image from "../assets/card2_image.webp";
import card3Image from "../assets/card3_image.webp";
import card4Image from "../assets/card4_image.webp";
import carousel1Image from "../assets/carousel_image1.webp"
import carousel2Image from "../assets/carousel_image2.webp"
import carousel3Image from "../assets/carousel_image3.webp"
import carousel4Image from "../assets/carousel_image4.webp"

function Hero() {
    const [isInAccount, setIsInAccount] = useState(false);
    const [scrollY, setScrollY] = useState(0);

    useEffect(() => {
        const checkAuth = () => {
            const token = getCookie("token");
            if (token) {
                setIsInAccount(true);
            } else {
                setIsInAccount(false);
            }
        }

        const handleScroll = () => {
            setScrollY(window.scrollY);
        };

        checkAuth();
        window.addEventListener('scroll', handleScroll);
        
        return () => window.removeEventListener('scroll', handleScroll);
    }, [])
    
    const parallaxStyle = {
        transform: `translateY(${scrollY * 0.5}px)`
    };
    
    return (
        <div id="main" className="bg-[url(assets/hero_image.jpg)] bg-cover h-screen md:h-240 bg-center relative overflow-hidden">
            <div 
                className="parallax absolute inset-0 bg-cover bg-center"
                style={parallaxStyle}
            ></div>
            <div className="bg-[var(--hero-shadow)] h-full w-full pt-32 md:pt-48 px-4 sm:px-8 md:px-48 flex flex-col relative z-10">
                <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-8xl font-bold text-[var(--neutral-color)] tracking-tight text-center md:text-start animate-fade-in-up">
                    Аналитика поля одним кликом
                </h1>
                <p className="text-lg sm:text-xl md:text-2xl lg:text-3xl text-[var(--neutral-color)] mt-4 md:mt-8 tracking-wider text-center md:text-start animate-fade-in-up" style={{animationDelay: '0.2s', animationFillMode: 'both'}}>
                    Просто укажите свой участок на карте — и наш искусственный<br className="hidden md:block" />
                    интеллект на основе спутниковых снимков мгновенно проведёт<br className="hidden md:block" />
                    диагностику. Получите готовый отчёт о состоянии почвы,<br className="hidden md:block" />
                    растительности и потенциальных рисках для вашего урожая.
                </p>

                <div className="flex-grow flex items-end justify-center pb-16 md:pb-48 animate-fade-in-up" style={{animationDelay: '0.4s', animationFillMode: 'both'}}>
                    <Link
                        to={isInAccount ? "/profile" : "/registration"}
                        className="bg-[var(--accent-color)] hover:bg-[var(--accent-light-color)]
                        transition-all duration-300 cursor-pointer rounded-full text-xl sm:text-2xl md:text-3xl lg:text-5xl px-6 py-4 md:px-8 md:py-6 text-[var(--neutral-color)] shadow-2xl text-center"
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

    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        const observer = new IntersectionObserver(
            ([entry]) => {
                if (entry.isIntersecting) {
                    setIsVisible(true);
                }
            },
            { threshold: 0.1 }
        );

        const section = document.getElementById('about-us');
        if (section) {
            observer.observe(section);
        }

        return () => {
            if (section) {
                observer.unobserve(section);
            }
        };
    }, []);

    return (
        <div id="about-us" className={`bg-[var(--neutral-color)] w-full section-fade-in ${isVisible ? 'section-visible' : ''}`}>
            <div className="container mx-auto px-4 sm:px-8 lg:px-16 pt-16 pb-32">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-y-16 lg:gap-x-32">
                    <h2 className="text-4xl sm:text-5xl md:text-6xl lg:text-8xl font-bold text-center lg:col-span-2 animate-fade-in-up">
                        О НАС
                    </h2>
                    <p className="text-lg sm:text-xl md:text-2xl lg:text-4xl text-start lg:col-span-2 tracking-wider text-center lg:text-start animate-fade-in-up" style={{animationDelay: '0.2s', animationFillMode: 'both'}}>
                        <strong>Мы создаём будущее сельского хозяйства,</strong> где технологии работают на результат
                        каждого фермера. Наша задача — дать вам не просто данные, а ясное понимание состояния ваших полей
                        и конкретные рекомендации для принятия решений. Всё, что для этого нужно, — всего несколько кликов.<br /><br />
                        <strong>Весь процесс от выбора поля до готового отчёта — прост и прозрачен</strong>
                    </p>

                    <div className="lg:row-start-3">
                        <h2 className="text-4xl sm:text-5xl md:text-6xl lg:text-9xl text-center text-[var(--neutral-dark-secondary-color)] mb-8 lg:mb-32 mt-8 lg:mt-16 animate-fade-in-left">
                            ШАГ 1 →
                        </h2>
                        <div className="flex justify-center animate-fade-in-up" style={{animationDelay: '0.3s', animationFillMode: 'both'}}>
                            <div>
                                <Card title="Получение снимков" description={card2Description} image={card2Image} />
                            </div>
                        </div>
                    </div>
                    <div className="lg:row-start-3">
                        <div className="flex justify-center animate-fade-in-up" style={{animationDelay: '0.5s', animationFillMode: 'both'}}>
                            <div>
                                <Card title="Выбор участка" description={card1Description} image={card1Image} />
                            </div>
                        </div>
                        <h2 className="text-4xl sm:text-5xl md:text-6xl lg:text-9xl text-center text-[var(--neutral-dark-secondary-color)] mb-8 lg:mb-32 mt-8 lg:mt-32 animate-fade-in-right">
                            ← ШАГ 2
                        </h2>
                    </div>
                    <div className="lg:row-start-4">
                        <h2 className="text-4xl sm:text-5xl md:text-6xl lg:text-9xl text-center text-[var(--neutral-dark-secondary-color)] mb-8 lg:mb-32 mt-8 lg:mt-16 animate-fade-in-left">
                            ШАГ 3 →
                        </h2>
                        <div className="flex justify-center animate-fade-in-up" style={{animationDelay: '0.7s', animationFillMode: 'both'}}>
                            <div>
                                <Card title="Подготовка отчета" description={card4Description} image={card4Image} />
                            </div>
                        </div>
                    </div>
                    <div className="lg:row-start-4">
                        <div className="flex justify-center animate-fade-in-up" style={{animationDelay: '0.9s', animationFillMode: 'both'}}>
                            <div>
                                <Card title="Анализ снимков" description={card3Description} image={card3Image} />
                            </div>
                        </div>
                        <h2 className="text-4xl sm:text-5xl md:text-6xl lg:text-9xl text-center text-[var(--neutral-dark-secondary-color)] mb-8 lg:mb-32 mt-8 lg:mt-32 animate-fade-in-right">
                            ← ШАГ 4
                        </h2>
                    </div>
                </div>
            </div>
        </div>
    );
}

function Advantages() {
    const [isInAccount, setIsInAccount] = useState(false);

    useEffect(() => {
        const checkAuth = () => {
            const token = getCookie("token");

            if (token) {
                setIsInAccount(true);
            }
            else {
                setIsInAccount(false);
            }
        }

        checkAuth();
    }, [])

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
                    to={isInAccount ? "/profile" : "/registration"}
                    className="bg-[var(--accent-color)] hover:bg-[var(--accent-light-color)]
                    transition-[background-color] duration-100 cursor-pointer rounded-full text-5xl px-8 py-6 text-[var(--neutral-color)] shadow-2xl"
                >
                    Анализировать поле
                </Link>
            </div>
        </div>
    );
}


export function Footer({ showNavigation=true, logoutFunction=() => {} }) {
    return (
        <footer className="bg-[var(--neutral-dark-color)] pt-8 md:pt-16 pb-8">
            <div className="max-w-7xl mx-auto px-4 sm:px-8">
                <div className="flex flex-col md:flex-row justify-between items-center gap-8 pb-8 border-b border-[var(--neutral-color)]">
                    <div className="flex flex-col items-center md:items-start text-center md:text-start">
                        <div className="flex items-center gap-4 mb-4">
                            <img src={logoSVG} alt="FieldScan" className="h-12 w-12 md:h-16 md:w-16" />
                            <span className="text-2xl md:text-4xl font-bold text-[var(--accent-color)] tracking-tight">FieldScan</span>
                        </div>
                        <span className="text-sm md:text-xl text-gray-500 font-medium mb-2">2025 © Все права защищены</span>
                        <span className="text-xs md:text-lg text-gray-400">Создано для будущего агроаналитики</span>
                    </div>
                    {showNavigation ? (
                        <nav className="flex flex-col md:flex-row gap-4 md:gap-6 items-center">
                            <a href="#main" className="text-lg md:text-2xl text-[var(--accent-color)] hover:text-[var(--accent-light-color)] transition-colors">
                                Главная
                            </a>
                            <a href="#about-us" className="text-lg md:text-2xl text-[var(--accent-color)] hover:text-[var(--accent-light-color)] transition-colors">
                                О нас
                            </a>
                            <a href="#advantages" className="text-lg md:text-2xl text-[var(--accent-color)] hover:text-[var(--accent-light-color)] transition-colors">
                                Преимущества
                            </a>
                        </nav>
                    ) : (
                        <nav className="flex flex-col md:flex-row gap-4 md:gap-6 items-center">
                            <Link to="/" className="text-lg md:text-2xl text-[var(--accent-color)] hover:text-[var(--accent-light-color)] transition-colors">
                                    Главная
                            </Link>
                            <button onClick={() => logoutFunction()} className="cursor-pointer text-lg md:text-2xl text-[var(--accent-color)] hover:text-[var(--accent-light-color)] transition-colors">
                                    Выйти
                            </button>
                        </nav>
                    )}
                </div>
                <div className="text-center text-gray-400 text-sm md:text-lg pt-6">
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