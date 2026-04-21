import React, { useState } from 'react';
import { Shield, Globe } from 'lucide-react';

const Header = ({ language, setLanguage }) => {
  const [isGlitching, setIsGlitching] = useState(false);

  return (
    <header style={{
      padding: '20px 40px',
      borderBottom: '2px solid #00ffcc',
      background: 'rgba(10, 10, 15, 0.95)',
      backdropFilter: 'blur(10px)',
      position: 'sticky',
      top: 0,
      zIndex: 100,
    }}>
      <div style={{
        maxWidth: '1400px',
        margin: '0 auto',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '20px',
      }}>
        <div 
          style={{ display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer' }}
          onMouseEnter={() => setIsGlitching(true)}
          onMouseLeave={() => setIsGlitching(false)}
        >
          <Shield size={40} color="#00ffcc" />
          <div>
            <h1 style={{
              fontSize: '28px',
              fontWeight: 'bold',
              letterSpacing: '2px',
              animation: isGlitching ? 'glitch 0.3s infinite' : 'none',
            }}>
              WARISNAMA<span style={{ color: '#ff00ff' }}>_AI</span>
            </h1>
            <p style={{ fontSize: '12px', color: '#888' }}>Pakistan's First Intelligent Inheritance System</p>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '24px', alignItems: 'center' }}>
          <nav style={{ display: 'flex', gap: '20px' }}>
            <a href="/" style={{ color: '#00ffcc', textDecoration: 'none' }}>Home</a>
            <a href="/calculator" style={{ color: '#fff', textDecoration: 'none' }}>Calculator</a>
          </nav>

          <button
            onClick={() => setLanguage(language === 'en' ? 'ur' : 'en')}
            style={{
              background: 'transparent',
              border: '1px solid #00ffcc',
              padding: '8px 16px',
              borderRadius: '8px',
              color: '#00ffcc',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}
          >
            <Globe size={16} />
            {language === 'en' ? 'اردو' : 'English'}
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;