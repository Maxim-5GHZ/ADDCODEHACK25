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
            <a href="#advantages" className={`${navButtonsStyle} text-3xl transition-colors duration-100"`}>
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

export default Header