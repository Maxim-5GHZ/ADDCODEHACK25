import React from 'react';
import { Link } from 'react-router-dom';

function BackButton() {
  return (
    <Link 
      to="/" 
      className="absolute text-lg sm:text-xl md:text-2xl lg:text-3xl self-start left-2 mx-4 sm:mx-8 md:mx-16 my-4 md:my-6 lg:my-8 hover:text-[var(--accent-dark-color)] transition-[color] duration-100"
    >
      ← На главную
    </Link>
  );
}

export default BackButton;