import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Parse scenario from natural language
export const parseScenario = async (inputText, language = 'urdu') => {
  const response = await api.post('/parse-scenario', { input_text: inputText, language });
  return response.data;
};

// Calculate inheritance shares
export const calculateShares = async (sect, heirs, totalEstate, debts = 0, wasiyyat = 0) => {
  const response = await api.post('/calculate-shares', { sect, heirs, total_estate: totalEstate, debts, wasiyyat });
  return response.data;
};

// Detect disputes
export const detectDisputes = async (scenarioData) => {
  const response = await api.post('/detect-disputes', scenarioData);
  return response.data;
};

// Calculate taxes
export const calculateHeirTax = async (shareValue, filerStatus, action, province = 'Punjab') => {
  const response = await api.post('/tax/calculate-heir', { share_value: shareValue, filer_status: filerStatus, action, province });
  return response.data;
};

// Generate certificate PDF
export const generateCertificate = async (data) => {
  const response = await api.post('/generate-certificate', data, { responseType: 'blob' });
  return response.data;
};

// Get process steps
export const getProcessSteps = async (minorHeir, hasDispute, sect, province) => {
  const response = await api.post('/process-navigator/steps', { minor_heir: minorHeir, has_dispute: hasDispute, sect, province });
  return response.data;
};

// What-if simulations
export const whatIfCompare = async (heirsShares, filerStatusMap, totalPropertyValue, province = 'Punjab') => {
  const response = await api.post('/whatif/compare', { heirs_shares: heirsShares, filer_status_map: filerStatusMap, total_property_value: totalPropertyValue, province });
  return response.data;
};

export default api;