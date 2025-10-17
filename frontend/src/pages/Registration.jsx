import { useEffect, useState, useRef } from "react"
import { Link, useNavigate } from "react-router-dom"
import logoImage from "../assets/logo.svg"
import { BarLoader } from "react-spinners"
import { getCookie, setCookie, isValidToken, deleteCookie } from "../utils/cookies"
import { registerUser, getToken } from "../utils/fetch"

function Registration() {
    const navigate = useNavigate();

    useEffect(() => {
        const checkAuth = async () => {
            const token = getCookie("token");
            if (token && isValidToken(token)) {
                try {
                    const isValid = await validateToken(token);
                    if (isValid) {
                        navigate("/profile");
                    } else {
                        deleteCookie("token");
                    }
                } catch (error) {
                    console.error("Token validation failed:", error);
                    deleteCookie("token");
                }
            }
        }
        checkAuth();
    }, [navigate])

    const [isButtonClicked, setIsButtonClicked] = useState(false);
    const [name, setName] = useState("");
    const [surname, setSurname] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [passwordAgain, setPasswordAgain] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState("")

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const passwordRegex = /^[A-Za-z0-9]{5,}$/;
    const nameRegex = /^[A-Za-zА-Яа-яЁё\s\-']{2,}$/;
    
    const isEmailValid = emailRegex.test(email);
    const isPasswordFormatValid = passwordRegex.test(password);
    const passwordsMatch = password === passwordAgain;
    const isNameValid = nameRegex.test(name);
    const isSurnameValid = nameRegex.test(surname);
    
    const emailError = isButtonClicked && !isEmailValid;
    const passwordFormatError = isButtonClicked && !isPasswordFormatValid;
    const passwordMatchError = isButtonClicked && !passwordsMatch;
    const nameError = isButtonClicked && !isNameValid;
    const surnameError = isButtonClicked && !isSurnameValid;

    const isFormValid = isNameValid && isSurnameValid && isEmailValid && isPasswordFormatValid && passwordsMatch;

    const handleRegistration = async () => {
        setIsButtonClicked(true);
        setError("");
        
        if (!isFormValid) {
            console.log("Форма невалидна, регистрация прервана");
            return;
        }
        
        setIsLoading(true);
        console.log("Регистрация...", { email, password });
        await register();
    }

    const register = async () => {
        try {
            const registrationResponse = await registerUser(email, password, name, surname);

            if (!registrationResponse.ok) {
                const errorText = await registrationResponse.text();
                throw new Error(errorText || 'Ошибка регистрации');
            }

            const tokenResponse = await getToken(email, password);

            if (!tokenResponse.ok) {
                const errorText = await tokenResponse.text();
                throw new Error(errorText || 'Ошибка получения токена');
            }

            const token = await tokenResponse.text();
            setCookie('token', token, 7);
            console.log("Регистрация успешна! Токен сохранен.");
            navigate("/profile");

        } catch (error) {
            console.error("Ошибка регистрации:", error);
            setError(error.message || "Произошла ошибка при регистрации");
        } finally {
            setIsLoading(false);
        }
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

    const getNameErrorMessage = () => {
        if (!name) return "Введите имя";
        if (name.length < 2) return "Имя должно содержать минимум 2 символа";
        return "Имя должно содержать только буквы, пробелы, дефисы и апострофы";
    }

    const getSurnameErrorMessage = () => {
        if (!surname) return "Введите фамилию";
        if (surname.length < 2) return "Фамилия должна содержать минимум 2 символа";
        return "Фамилия должна содержать только буквы, пробелы, дефисы и апострофы";
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
                            <label htmlFor="user-name" className="text-2xl md:text-3xl ml-4 mb-2 text-[var(--neutral-dark-color)]">
                                Имя
                            </label>
                            <input 
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                id="user-name" 
                                name="user-name" 
                                type="text" 
                                placeholder="Иван" 
                                className={`text-2xl md:text-3xl bg-[var(--neutral-color)] rounded-4xl py-4 px-6 shadow-2xs 
                                focus:outline-0 focus:ring-2 w-full ${
                                    nameError 
                                    ? "outline-1 outline-red-500 focus:ring-red-500" 
                                    : "focus:ring-[var(--accent-color)]"
                                }`}
                            />
                            {nameError && (
                                <span className="text-red-500 text-xl mt-2 ml-4">
                                    {getNameErrorMessage()}
                                </span>
                            )}
                        </div>

                        <div className="flex flex-col w-full">
                            <label htmlFor="user-surname" className="text-2xl md:text-3xl ml-4 mb-2 text-[var(--neutral-dark-color)]">
                                Фамилия
                            </label>
                            <input 
                                value={surname}
                                onChange={(e) => setSurname(e.target.value)}
                                id="user-surname" 
                                name="user-surname" 
                                type="text" 
                                placeholder="Иванов" 
                                className={`text-2xl md:text-3xl bg-[var(--neutral-color)] rounded-4xl py-4 px-6 shadow-2xs 
                                focus:outline-0 focus:ring-2 w-full ${
                                    surnameError 
                                    ? "outline-1 outline-red-500 focus:ring-red-500" 
                                    : "focus:ring-[var(--accent-color)]"
                                }`}
                            />
                            {surnameError && (
                                <span className="text-red-500 text-xl mt-2 ml-4">
                                    {getSurnameErrorMessage()}
                                </span>
                            )}
                        </div>

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