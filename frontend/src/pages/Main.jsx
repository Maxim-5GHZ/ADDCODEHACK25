import { useState, useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import Header from "../components/Header";
import Card from "../components/Card";
import card1Image from "../assets/card1_image.jpg";
import card2Image from "../assets/card2_image.jpg";
import card3Image from "../assets/card3_image.jpg";
import card4Image from "../assets/card4_image.jpg";

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
        <div id="about-us" className="bg-[var(--neutral-color)]">
            <div className="md:container mx-auto w-full lg:w-[max(2/3vw, 1000px)] pt-16 pb-32">
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
    const items = [
        {
            img: card1Image,
            title: "Точность и скорость",
            desc: "Мгновенный анализ спутниковых снимков и высокая детализация отчётов для принятия решений без задержек."
        },
        {
            img: card2Image,
            title: "Простота использования",
            desc: "Интуитивный интерфейс: всё, что нужно — выбрать участок и получить результат. Без лишних действий."
        },
        {
            img: card3Image,
            title: "Экономия ресурсов",
            desc: "Сокращение затрат на агрономию и мониторинг — вы платите только за результат и получаете максимум пользы."
        },
        {
            img: card4Image,
            title: "Актуальные рекомендации",
            desc: "Персональные советы по уходу за полем, основанные на реальных данных и современных технологиях."
        }
    ];

    const [active, setActive] = useState(0);
    const intervalRef = useRef(null);

    useEffect(() => {
        intervalRef.current = setInterval(() => {
            setActive(prev => (prev + 1) % items.length);
        }, 3500);

        return () => clearInterval(intervalRef.current);
    }, [items.length]);

    return (
        <div id="advantages" className="bg-gradient-to-br from-[#eafaf3] to-[#f6f6f6] py-32">
            <div className="max-w-4xl mx-auto px-4">
                <h2 className="text-7xl font-bold text-center text-[#009e4f] mb-20 tracking-tight drop-shadow-lg">
                    Преимущества
                </h2>
                <div className="relative flex justify-center items-center h-[520px]">
                    {items.map((item, idx) => (
                        <div
                            key={idx}
                            className={`absolute left-0 right-0 mx-auto transition-opacity duration-700 ${
                                active === idx ? "opacity-100 z-10" : "opacity-0 z-0"
                            }`}
                            style={{ width: "100%", maxWidth: "600px", height: "520px" }}
                        >
                            <div className="bg-white rounded-3xl shadow-2xl p-12 flex flex-col items-center text-center h-full justify-center">
                                <img
                                    src={item.img}
                                    alt={item.title}
                                    className="rounded-2xl mb-8 object-cover w-full h-64 shadow-lg"
                                />
                                <div className="text-3xl font-bold text-[#009e4f] mb-6">{item.title}</div>
                                <div className="text-xl text-gray-600">{item.desc}</div>
                            </div>
                        </div>
                    ))}
                    <div className="absolute bottom-8 left-0 right-0 flex justify-center gap-3">
                        {items.map((_, idx) => (
                            <span
                                key={idx}
                                className={`w-4 h-4 rounded-full transition-all duration-300 ${
                                    active === idx ? "bg-[#009e4f]" : "bg-[#b2e3c7]"
                                }`}
                            />
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}

function Footer() {
    return (
        <footer className="bg-gradient-to-br from-[#eafaf3] to-[#d2f5e6] pt-16 pb-8 mt-24">
            <div className="max-w-7xl mx-auto px-8">
                <div className="flex flex-col md:flex-row justify-between items-center gap-8 pb-8 border-b border-[#b2e3c7]">
                    <div className="flex flex-col items-start">
                        <div className="flex items-center gap-4 mb-4">
                            <img src="/logo192.png" alt="FieldScan" className="h-12 w-12" />
                            <span className="text-4xl font-bold text-[#009e4f] tracking-tight">FieldScan</span>
                        </div>
                        <span className="text-xl text-gray-500 font-medium mb-2">2025 © Все права защищены</span>
                        <span className="text-lg text-gray-400">Создано для будущего агроаналитики</span>
                    </div>
                    <nav className="flex flex-col md:flex-row gap-6 items-center">
                        <a href="#main" className="text-2xl font-bold text-[#009e4f] hover:text-[#00c97b] transition-colors">Главная</a>
                        <a href="#about-us" className="text-2xl font-bold text-[#009e4f] hover:text-[#00c97b] transition-colors">О нас</a>
                        <a href="#advantages" className="text-2xl font-bold text-[#009e4f] hover:text-[#00c97b] transition-colors">Преимущества</a>
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
