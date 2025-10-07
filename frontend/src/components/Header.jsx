import { Link } from "react-router-dom";
import { useState, useEffect } from "react";
import logoSVG from "../assets/logo.svg"
// import { getCookie } from "../utils/cookies";

function Header({ isTransparent }) {
    const [user, setUser] = useState(null);
    let navButtonsStyle = isTransparent ? "text-[var(--neutral-color)] hover:text-[var(--accent-light-color)]" : "text-[var(--neutral-dark-color)] hover:text-[var(--accent-dark-color)]"

    useEffect(() => {
        const checkAuth = () => {
            // const token = getCookie('token');
            const token = true; // Временная заглушка
            
            if (token) {
                // Временная заглушка
                setUser({
                    name: "Иван",
                    surname: "Иванов"
                });
            } else {
                setUser(null);
            }
        };

        checkAuth();
    }, []);

    return (
    <header id='header' className={`shadow-md fixed w-dvw h-1/14 z-20 ${isTransparent ? "bg-[var(--header-blur)] backdrop-blur-xs" : "bg-[var(--neutral-color)]" }`}>
        <div className="px-32 h-full">
            <div className="flex items-center justify-between h-full">
                <div className="flex flex-row flex-shrink-0 h-full items-center">
                    <Link to="/" className="flex items-center h-full">
                        <img src={logoSVG} className="max-h-full" />
                    </Link>
                    <Link to="/" className={`text-4xl poppins-medium mt-2
                        ${isTransparent ? "text-[var(--neutral-color)]" : "text-[var(--neutral-dark-color)]"}`}>
                            FieldScan
                    </Link>
                </div>

                <nav className="hidden md:flex gap-x-16 text-center">
                    <a href="#main" className={`${navButtonsStyle} text-3xl transition-colors duration-100`}>
                        Главная
                    </a>
                    <a href="#about-us" className={`${navButtonsStyle} text-3xl transition-colors duration-100"`}>
                        О нас
                    </a>
                    <a href="#advantages" className={`${navButtonsStyle} text-3xl transition-colors duration-100"`}>
                        Преимущества
                    </a>
                </nav>

                <div className="flex items-center gap-x-16">
                    {user ? (
                        <Link to="/profile" className={`${navButtonsStyle} text-3xl`}>
                            {user.name} {user.surname}
                        </Link>
                    ) : (
                        <>
                            <Link to="/login" className={`${navButtonsStyle} text-3xl transition-colors duration-100"`}>
                                Войти
                            </Link>
                            <Link to="/registration" className={`${navButtonsStyle} text-3xl transition-colors duration-100"`}>
                                Зарегистрироваться
                            </Link>
                        </>
                    )}
                </div>
            </div>
        </div>
    </header>
    );
}

export default Header