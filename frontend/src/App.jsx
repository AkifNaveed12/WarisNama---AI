import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import CyberpunkBackground from './components/Layout/CyberpunkBackground';
import Header from './components/Layout/Header';
import Home from './pages/Home';
import Calculator from './pages/Calculator';
import './styles/global.css';

function App() {
  const [language, setLanguage] = useState('en');

  return (
    <Router>
      <CyberpunkBackground />
      <Header language={language} setLanguage={setLanguage} />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/calculator" element={<Calculator />} />
      </Routes>
    </Router>
  );
}

export default App;