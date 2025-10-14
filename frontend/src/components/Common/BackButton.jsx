import React from 'react';
import { Link } from 'react-router-dom';

function BackButton() {
  return (
    <Link 
      to="/" 
      className="absolute text-2xl md:text-3xl self-start left-2 mx-16 my-8 hover:text-[var(--accent-dark-color)] transition-[color] duration-100">
      ← На главную
    </Link>
  );
}

export default BackButton;
