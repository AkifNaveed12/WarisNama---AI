import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Mic, Send, AlertCircle, TrendingUp, FileText, Shield } from 'lucide-react';
import { parseScenario } from '../services/api';

const Home = () => {
  const navigate = useNavigate();
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [language, setLanguage] = useState('en');

  const handleSubmit = async () => {
    if (!inputText.trim()) return;
    
    setIsLoading(true);
    try {
      const result = await parseScenario(inputText, language);
      navigate('/calculator', { state: { parsedData: result, inputText } });
    } catch (error) {
      console.error('Parse error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const stats = [
    { icon: <AlertCircle size={24} />, value: '2M+', label: 'Pending Cases' },
    { icon: <TrendingUp size={24} />, value: '60s', label: 'Resolution Time' },
    { icon: <FileText size={24} />, value: '4', label: 'Legal Systems' },
    { icon: <Shield size={24} />, value: '7', label: 'Fraud Patterns' },
  ];

  return (
    <div className="cyberpunk-container">
      <div style={{ textAlign: 'center', padding: '60px 20px' }}>
        <h1 style={{
          fontSize: '64px',
          fontWeight: 'bold',
          background: 'linear-gradient(135deg, #00ffcc 0%, #ff00ff 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          marginBottom: '20px',
        }}>
          WARISNAMA AI
        </h1>
        <p style={{ fontSize: '20px', color: '#ccc', marginBottom: '40px' }}>
          Pakistan's First Intelligent Inheritance Dispute Resolution System
        </p>

        {/* Stats */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '20px',
          marginBottom: '60px',
        }}>
          {stats.map((stat, i) => (
            <div key={i} className="cyberpunk-card" style={{ textAlign: 'center' }}>
              <div style={{ color: '#00ffcc', marginBottom: '12px' }}>{stat.icon}</div>
              <div style={{ fontSize: '36px', fontWeight: 'bold', color: '#fff' }}>{stat.value}</div>
              <div style={{ color: '#888' }}>{stat.label}</div>
            </div>
          ))}
        </div>

        {/* Input Section */}
        <div className="cyberpunk-card" style={{ maxWidth: '800px', margin: '0 auto' }}>
          <h2 style={{ marginBottom: '20px' }}>Describe Your Situation</h2>
          <textarea
            className="cyberpunk-input"
            rows="5"
            placeholder={language === 'en' 
              ? "Example: My father passed away. He had 2 sons, 3 daughters, and 1 wife. He owned a house worth 80 lakh rupees."
              : "مثال: میرے والد کا انتقال ہو گیا۔ ان کے 2 بیٹے، 3 بیٹیاں اور 1 بیوی تھی۔ ان کے پاس 80 لاکھ روپے کا مکان تھا۔"}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            style={{ marginBottom: '20px' }}
          />
          <div style={{ display: 'flex', gap: '16px', justifyContent: 'center' }}>
            <button className="cyberpunk-button" onClick={handleSubmit} disabled={isLoading}>
              {isLoading ? 'Processing...' : <><Send size={18} style={{ marginRight: '8px' }} /> Calculate</>}
            </button>
            <button className="cyberpunk-button" style={{ borderColor: '#ff00ff', color: '#ff00ff' }}>
              <Mic size={18} style={{ marginRight: '8px' }} /> Voice Input
            </button>
          </div>
        </div>

        {/* Critical Info Banner */}
        <div style={{
          marginTop: '40px',
          padding: '20px',
          background: 'rgba(0, 255, 204, 0.1)',
          borderLeft: '4px solid #00ffcc',
          borderRadius: '8px',
        }}>
          <p style={{ color: '#00ffcc' }}>
            ⚡ Pakistan has <strong>ZERO inheritance tax</strong>. Don't let this fear delay your family's rightful shares.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Home;