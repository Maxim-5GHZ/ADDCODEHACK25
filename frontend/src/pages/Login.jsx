import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Link } from "react-router-dom"
import logoImage from "../assets/logo.svg"
import { getCookie, setCookie, isValidToken } from "../utils/cookies";
import { getToken, validateToken } from "../utils/fetch";
import { BarLoader } from "react-spinners";

function Login() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState("");

    const navigate = useNavigate();
    
    useEffect(() => {
        const checkAuth = async () => {
            const token = getCookie("token");
            console.log(`Token: ${token}`)

            if (token && isValidToken(token)) {
                try {
                    // Дополнительная проверка токена на сервере
                    const isValid = await validateToken(token);
                    if (isValid) {
                        navigate("/profile");   
                    } else {
                        // Токен невалиден, удаляем его
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

    const handleLogin = async () => {
        try{
            setIsLoading(true);
            setError("");
            const token = await getToken(email, password);
            
            // Проверяем, что токен валиден перед сохранением
            if (token && isValidToken(token)) {
                setCookie("token", token, 7);
                navigate("/profile");
            } else {
                throw new Error("Получен невалидный токен от сервера");
            }
        }
        catch (error) {
            setIsLoading(false);
            setError(error.message || "Ошибка входа. Проверьте email и пароль.");
            console.log("Login error:", error);
        }
        finally {
            setIsLoading(false);
        }
    }
    
    return (
        <>
            <div className="absolute h-[100vh] w-[100vw] bg-[var(--neutral-color)] -z-1">
            </div>
            <div className="flex bg-[var(--neutral-color)] justify-center items-center">
                <Link to="/" className="absolute text-2xl md:text-3xl self-start left-2 mx-16 my-8 hover:text-[var(--accent-dark-color)] transition-[color] duration-100">
                    ← На главную
                </Link>
                <Link to="/registration" className="absolute text-2xl md:text-3xl self-start right-2 mx-16 my-8 hover:text-[var(--accent-dark-color)] transition-[color] duration-100">
                    Регистрация аккаунта →
                </Link>
                <div className="bg-[var(--neutral-secondary-color)] w-2/3 h-3/4 sm:w-1/2 max-w-240 rounded-[2vw] shadow-xl p-16 space-y-16 mt-[25vh] md:mt-[13vh]">
                    <div className="flex justify-center items-center space-x-4">
                        <img src={logoImage} className="w-1/10 h-1/10"/>
                        <h1 className="text-5xl md:text-6xl text-center font-bold tracking-tight">
                            Вход
                        </h1>
                    </div>
                    
                    {/* Показываем ошибку, если есть */}
                    {error && (
                        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                            {error}
                        </div>
                    )}
                    
                    <form method="post" className="flex flex-col justify-center space-y-8">
                        <div className="flex flex-col w-full">
                            <label htmlFor="email" className="text-2xl md:text-3xl ml-4 mb-2 text-[var(--neutral-dark-color)]">
                                Почта
                            </label>
                            <input onChange={(e) => setEmail(e.target.value)} id="email" name="email" type="email" placeholder="Ваша@почта.ru" 
                            className="text-2xl md:text-3xl bg-[var(--neutral-color)] rounded-4xl py-4 px-6 shadow-2xs 
                            focus:ring-[var(--accent-color)] focus:outline-0 focus:ring-2 w-full"/>
                        </div>
                        <div className="flex flex-col w-full">
                            <label htmlFor="password" className="text-2xl md:text-3xl ml-4 mb-2 text-[var(--neutral-dark-color)]">
                                Пароль
                            </label>
                            <input onChange={(e) => setPassword(e.target.value)} id="password" name="password" type="password" placeholder="Ваш секретный пароль" 
                            className="text-2xl md:text-3xl bg-[var(--neutral-color)] rounded-4xl py-4 px-6 shadow-2xs 
                            focus:ring-[var(--accent-color)] focus:outline-0 focus:ring-2 w-full"/>
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
                                <input onClick={handleLogin} type="button" value="Войти" className="bg-[var(--accent-color)] hover:bg-[var(--accent-light-color)]
                                transition-[background-color] duration-100 cursor-pointer rounded-full text-2xl md:text-3xl px-5 py-5 text-[var(--neutral-color)] 
                                shadow-2xs w-3/4"/>
                            )}
                        </div>
                        <p className="text-end self-end">
                            Забыли пароль? <span className="text-[var(--accent-dark-color)] cursor-pointer">Восстановить пароль</span>
                        </p>
                    </form>
                </div>
            </div> 
        </>
    )
}

export default Login