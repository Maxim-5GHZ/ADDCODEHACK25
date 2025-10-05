import { useState, useRef } from "react"
import { Link } from "react-router-dom"
import logoImage from "../assets/logo.svg"
import { BarLoader } from "react-spinners"

function Registration() {
    const [isButtonClicked, setIsButtonClicked] = useState(false);
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [passwordAgain, setPasswordAgain] = useState("");
    const [isLoading, setIsLoading] = useState(false);

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const passwordRegex = /^[A-Za-z0-9]{5,}$/;
    
    const isEmailValid = emailRegex.test(email);
    const isPasswordFormatValid = passwordRegex.test(password);
    const passwordsMatch = password === passwordAgain;
    
    const emailError = isButtonClicked && !isEmailValid;
    const passwordFormatError = isButtonClicked && !isPasswordFormatValid;
    const passwordMatchError = isButtonClicked && !passwordsMatch;

    const isFormValid = isEmailValid && isPasswordFormatValid && passwordsMatch;

    const handleRegistration = async () => {
        setIsButtonClicked(true);
        
        if (!isFormValid) {
            console.log("Форма невалидна, регистрация прервана");
            return;
        }
        
        setIsLoading(true);
        console.log("Регистрация...", { email, password });
        
    }

    const registerUser = async () => {
        fetch()
    }

    const getEmailErrorMessage = () => {
        if (!email) return "Введите email";
        return "Введите корректный email (например: my@mail.com)";
    }

    const getPasswordErrorMessage = () => {
        if (!password) return "Введите пароль";
        if (password.length < 5) return "Пароль должен содержать минимум 5 символов";
        return "Пароль должен содержать только буквы и цифры";
    }

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
                    <form method="post" className="flex flex-col justify-center space-y-8">
                        <div className="flex flex-col w-full">
                            <label htmlFor="email" className="text-2xl md:text-3xl ml-4 mb-2 text-[var(--neutral-dark-color)]">
                                Почта
                            </label>
                            <input 
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                id="email" 
                                name="email" 
                                type="email" 
                                placeholder="Ваша@почта.ru" 
                                className={`text-2xl md:text-3xl bg-[var(--neutral-color)] rounded-4xl py-4 px-6 shadow-2xs 
                                focus:outline-0 focus:ring-2 w-full ${
                                    emailError 
                                    ? "outline-1 outline-red-500 focus:ring-red-500" 
                                    : "focus:ring-[var(--accent-color)]"
                                }`}
                            />
                            {emailError && (
                                <span className="text-red-500 text-xl mt-2 ml-4">
                                    {getEmailErrorMessage()}
                                </span>
                            )}
                        </div>

                        <div className="flex flex-col w-full">
                            <label htmlFor="password" className="text-2xl md:text-3xl ml-4 mb-2 text-[var(--neutral-dark-color)]">
                                Пароль
                            </label>
                            <input 
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                id="password" 
                                name="password" 
                                type="password" 
                                placeholder="Ваш секретный пароль" 
                                className={`text-2xl md:text-3xl bg-[var(--neutral-color)] rounded-4xl py-4 px-6 shadow-2xs 
                                focus:outline-0 focus:ring-2 w-full ${
                                    passwordFormatError 
                                    ? "outline-1 outline-red-500 focus:ring-red-500" 
                                    : "focus:ring-[var(--accent-color)]"
                                }`}
                            />
                            {passwordFormatError && (
                                <span className="text-red-500 text-xl mt-2 ml-4">
                                    {getPasswordErrorMessage()}
                                </span>
                            )}
                        </div>

                        <div className="flex flex-col w-full">
                            <label htmlFor="password-again" className="text-2xl md:text-3xl ml-4 mb-2 text-[var(--neutral-dark-color)]">
                                Пароль ещё раз
                            </label>
                            <input 
                                value={passwordAgain}
                                onChange={(e) => setPasswordAgain(e.target.value)}
                                id="password-again" 
                                type="password" 
                                placeholder="Введите ваш пароль ещё раз" 
                                className={`text-2xl md:text-3xl bg-[var(--neutral-color)] rounded-4xl py-4 px-6 shadow-2xs 
                                focus:outline-0 focus:ring-2 w-full ${
                                    passwordMatchError 
                                    ? "outline-1 outline-red-500 focus:ring-red-500" 
                                    : "focus:ring-[var(--accent-color)]"
                                }`}
                            />
                            {passwordMatchError && (
                                <span className="text-red-500 text-xl mt-2 ml-4">
                                    Пароли не совпадают
                                </span>
                            )}
                        </div>

                        <div className="flex justify-center items-center mt-16">
                            {isLoading ? (
                                <div className="flex justify-center items-center w-1/2 rounded-full bg-[var(--neutral-dark-secondary-color)]">
                                    <BarLoader
                                        color="var(--accent-color)"
                                        loading={isLoading}
                                        width="100%"
                                        height={5}
                                        aria-label="Регистрация..."
                                    />
                                </div>
                            ) : (
                                <input 
                                    onClick={handleRegistration} 
                                    name="registration-button" 
                                    type="button" 
                                    value="Зарегистрироваться" 
                                    disabled={isButtonClicked && !isFormValid}
                                    className={`${
                                        isButtonClicked && !isFormValid 
                                        ? "bg-gray-400 cursor-not-allowed" 
                                        : "bg-[var(--accent-color)] hover:bg-[var(--accent-light-color)] cursor-pointer"
                                    } transition-[background-color] duration-100 rounded-full text-2xl md:text-3xl px-5 py-5 text-[var(--neutral-color)] shadow-2xs w-3/4`}
                                />
                            )}
                        </div>
                    </form>
                </div>
            </div> 
        </>
    )
}

export default Registration