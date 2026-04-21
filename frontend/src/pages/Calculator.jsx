import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';
import { Download } from 'lucide-react';
import { calculateShares, generateCertificate } from '../services/api';

const COLORS = ['#00ffcc', '#ff00ff', '#ffcc00', '#00ccff', '#ff6666', '#66ff66'];

const Calculator = () => {
  const location = useLocation();
  const { parsedData } = location.state || {};
  
  const [sect, setSect] = useState('hanafi');
  const [heirs, setHeirs] = useState({});
  const [totalEstate, setTotalEstate] = useState(0);
  const [debts, setDebts] = useState(0);
  const [wasiyyat, setWasiyyat] = useState(0);
  const [shares, setShares] = useState(null);
  const [loading, setLoading] = useState(false);

  // Initialize from parsed data
  useEffect(() => {
    if (parsedData) {
      const heirsMap = {};
      parsedData.heirs?.forEach(heir => {
        heirsMap[heir.type + 's'] = (heirsMap[heir.type + 's'] || 0) + heir.count;
      });
      setHeirs(heirsMap);
      
      const assetValue = parsedData.assets?.reduce((sum, a) => sum + (a.estimated_value_pkr || 0), 0) || 0;
      setTotalEstate(assetValue);
      
      if (parsedData.sect_mentioned) setSect(parsedData.sect_mentioned);
    }
  }, [parsedData]);

  const handleCalculate = async () => {
    setLoading(true);
    try {
      const result = await calculateShares(sect, heirs, totalEstate, debts, wasiyyat);
      setShares(result.shares);
    } catch (error) {
      console.error('Calculation error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadCertificate = async () => {
    if (!shares) return;
    const blob = await generateCertificate({
      deceased_name: parsedData?.deceased?.relation || 'Deceased',
      sect,
      total_estate: totalEstate,
      debts,
      wasiyyat,
      shares,
      language: 'en',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `inheritance_certificate_${Date.now()}.pdf`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const chartData = shares ? Object.entries(shares).map(([name, data]) => ({
    name: name.replace(/_/g, ' '),
    value: data.amount,
    fraction: data.fraction,
  })) : [];

  // Fix: Calculate max wasiyyat as a variable
  const maxWasiyyat = Math.floor(totalEstate / 3);
  const formattedMaxWasiyyat = maxWasiyyat.toLocaleString();

  return (
    <div className="cyberpunk-container">
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        {/* Input Panel */}
        <div className="cyberpunk-card">
          <h2 style={{ marginBottom: '20px' }}>📝 Inheritance Details</h2>
          
          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', marginBottom: '8px', color: '#00ffcc' }}>Legal System</label>
            <select className="cyberpunk-select" value={sect} onChange={(e) => setSect(e.target.value)} style={{ width: '100%' }}>
              <option value="hanafi">Sunni Hanafi (75% of Pakistan)</option>
              <option value="shia">Shia Jafari (20% of Pakistan)</option>
              <option value="christian">Christian (Succession Act 1925)</option>
              <option value="hindu">Hindu (Hindu Succession Act 1956)</option>
            </select>
          </div>

          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', marginBottom: '8px', color: '#00ffcc' }}>Total Estate (PKR)</label>
            <input className="cyberpunk-input" type="number" value={totalEstate} onChange={(e) => setTotalEstate(Number(e.target.value))} />
          </div>

          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', marginBottom: '8px', color: '#00ffcc' }}>Debts (PKR)</label>
            <input className="cyberpunk-input" type="number" value={debts} onChange={(e) => setDebts(Number(e.target.value))} />
          </div>

          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', marginBottom: '8px', color: '#00ffcc' }}>Wasiyyat (Will) (PKR)</label>
            <input className="cyberpunk-input" type="number" value={wasiyyat} onChange={(e) => setWasiyyat(Number(e.target.value))} />
            <small style={{ color: '#888' }}>Max 1/3 of estate: {formattedMaxWasiyyat} PKR</small>
          </div>

          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', marginBottom: '8px', color: '#00ffcc' }}>Heirs</label>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              {['sons', 'daughters', 'wife', 'husband', 'mother', 'father', 'brothers', 'sisters'].map(heirType => (
                <div key={heirType}>
                  <label style={{ fontSize: '12px', color: '#888' }}>{heirType}</label>
                  <input
                    className="cyberpunk-input"
                    type="number"
                    min="0"
                    value={heirs[heirType] || 0}
                    onChange={(e) => setHeirs({ ...heirs, [heirType]: parseInt(e.target.value) || 0 })}
                    style={{ padding: '8px' }}
                  />
                </div>
              ))}
            </div>
          </div>

          <button className="cyberpunk-button" onClick={handleCalculate} disabled={loading} style={{ width: '100%' }}>
            {loading ? 'Calculating...' : '⚡ Calculate Shares'}
          </button>
        </div>

        {/* Results Panel */}
        <div className="cyberpunk-card">
          <h2 style={{ marginBottom: '20px' }}>📊 Inheritance Distribution</h2>
          
          {shares && !shares.error ? (
            <>
              {chartData.length > 0 && (
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie data={chartData} cx="50%" cy="50%" outerRadius={80} dataKey="value" label={({ name }) => name}>
                      {chartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => `PKR ${value.toLocaleString()}`} />
                  </PieChart>
                </ResponsiveContainer>
              )}
              
              <div style={{ marginTop: '20px', maxHeight: '300px', overflowY: 'auto' }}>
                {Object.entries(shares).map(([heir, data]) => (
                  <div key={heir} style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    padding: '12px',
                    borderBottom: '1px solid rgba(0, 255, 204, 0.2)',
                  }}>
                    <span style={{ fontWeight: 'bold' }}>{heir.replace(/_/g, ' ')}</span>
                    <span style={{ color: '#00ffcc' }}>{data.fraction}</span>
                    <span>PKR {data.amount?.toLocaleString()}</span>
                  </div>
                ))}
              </div>
              
              <button onClick={handleDownloadCertificate} className="cyberpunk-button" style={{ width: '100%', marginTop: '20px' }}>
                <Download size={18} style={{ marginRight: '8px' }} /> Download Share Certificate
              </button>
            </>
          ) : (
            <div style={{ textAlign: 'center', padding: '40px', color: '#888' }}>
              {shares?.error || 'Enter details and click Calculate'}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Calculator;