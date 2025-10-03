import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Main from './pages/Main'
import Login from './pages/Login'
import Registration from './pages/Registration'
import Profile from './pages/Profile'
import './App.css'

function App() {
  return (
    <>
    <Router>
      <Routes>
        <Route path="/" element={ <Main/> }/>
        <Route path="/login" element={ <Login/> }/>
        <Route path="/registration" element={ <Registration/> }/>
        <Route path="/profile" element={ <Profile/> }/>
        <Route path="*" element={ <Main/> }/>
      </Routes>
    </Router>
    </>
  )
}

export default App