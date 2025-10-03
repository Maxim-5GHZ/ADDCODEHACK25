import { Link } from "react-router-dom"
import logoImage from "../assets/logo.svg"

function Registration() {
    return (
        <>
            <div className="absolute h-[100vh] w-[100vw] bg-[var(--neutral-color)] -z-1">
            </div>
            <div className="flex bg-[var(--neutral-color)] justify-center items-center">
                <Link to="/" className="absolute text-2xl md:text-3xl self-start left-2 mx-16 my-8 hover:text-[var(--accent-dark-color)] transition-[color] duration-100">
                    ← На главную
                </Link>
                <Link to="/login" className="absolute text-2xl md:text-3xl self-start right-2 mx-16 my-8 hover:text-[var(--accent-dark-color)] transition-[color] duration-100">
                    Вход в аккаунт →
                </Link>
                <div className="bg-[var(--neutral-secondary-color)] w-2/3 h-3/4 sm:w-1/2 max-w-240 rounded-[2vw] shadow-xl p-16 space-y-16 mt-[25vh] md:mt-[13vh]">
                    <div className="flex justify-center items-center space-x-4">
                        <img src={logoImage} className="w-1/10 h-1/10"/>
                        <h1 className="text-5xl md:text-6xl text-center font-bold tracking-tight">
                            Регистрация
                        </h1>
                    </div>
                    <form method="post" className="flex flex-col justify-center space-y-16">
                        <div className="flex flex-col w-full">
                            <label for="email" className="text-2xl md:text-3xl ml-4 mb-2 text-[var(--neutral-dark-color)]">
                                Почта
                            </label>
                            <input id="email" name="email" type="email" placeholder="Ваша@почта.ru" 
                            className="text-2xl md:text-3xl bg-[var(--neutral-color)] rounded-4xl py-4 px-6 shadow-2xs 
                            focus:ring-[var(--accent-color)] focus:outline-0 focus:ring-2 w-full"/>
                        </div>
                        <div className="flex flex-col w-full">
                            <label for="password" className="text-2xl md:text-3xl ml-4 mb-2 text-[var(--neutral-dark-color)]">
                                Пароль
                            </label>
                            <input id="password" name="password" type="password" placeholder="Ваш секретный пароль" 
                            className="text-2xl md:text-3xl bg-[var(--neutral-color)] rounded-4xl py-4 px-6 shadow-2xs 
                            focus:ring-[var(--accent-color)] focus:outline-0 focus:ring-2 w-full"/>
                        </div>
                        <div className="flex flex-col w-full">
                            <label for="password-again" className="text-2xl md:text-3xl ml-4 mb-2 text-[var(--neutral-dark-color)]">
                                Пароль ещё раз
                            </label>
                            <input id="password-again" type="password" placeholder="Введите ваш пароль ещё раз" 
                            className="text-2xl md:text-3xl bg-[var(--neutral-color)] rounded-4xl py-4 px-6 shadow-2xs 
                            focus:ring-[var(--accent-color)] focus:outline-0 focus:ring-2 w-full"/>
                        </div>
                        <div className="flex justify-center items-center mt-8">
                            <input type="button" value="Зарегистрироваться" className="bg-[var(--accent-color)] hover:bg-[var(--accent-light-color)]
                                transition-[background-color] duration-100 cursor-pointer rounded-full text-2xl md:text-3xl px-5 py-5 text-[var(--neutral-color)] 
                                shadow-2xs w-3/4"/>
                        </div>
                        <p className="text-end self-end">
                            Забыли пароль? <span className="text-[var(--accent-dark-color)]">Восстановить пароль</span>
                        </p>
                    </form>
                </div>
            </div> 
        </>
    )
}

export default Registration