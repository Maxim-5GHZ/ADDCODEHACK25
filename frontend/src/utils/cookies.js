export const setCookie = (name, value, days = 30) => {
  const expires = new Date();
  expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000);
  document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/`;
};

export const getCookie = (name) => {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
};

export const deleteCookie = (name) => {
  document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/`;
};

export const isValidToken = (token) => {
  if (!token) return false;
  
  try {
    // Если токен в формате JWT
    if (token.split('.').length === 3) {
      return true;
    }
    // Другие проверки
    return token.length > 10;
  } catch {
    return false;
  }
};