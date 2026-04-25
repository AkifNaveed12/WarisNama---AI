// import api from './api'

// export const endpoints = {
//   calculateShares: (data) => api.post('/calculate/', data),
//   parseNLP: (text) => api.post('/nlp/parse', { text }),
//   detectDisputes: (flags) => api.post('/dispute/detect', { flags }),
//   calculateTax: (data) => api.post('/tax/calculate', data),
//   chat: (message, sessionId = null) => api.post('/chat/', { message, session_id: sessionId }),
//   generateShareCertificate: (data) => api.post('/documents/share-certificate', data, { responseType: 'blob' }),
//   generateLegalNotice: (data) => api.post('/documents/legal-notice', data, { responseType: 'blob' }),
//   generateFIR: (data) => api.post('/documents/fir', data, { responseType: 'blob' }),
// }


import api from './api'

export const endpoints = {
  calculateShares: (data) => api.post('/calculate/', data),
  parseNLP: (text) => api.post('/nlp/parse', { text }),
  detectDisputes: (flags) => api.post('/dispute/detect', { flags }),
  calculateTax: (data) => api.post('/tax/calculate', data),
  getProcessSteps: (hasMinor, hasDispute, isSelling) =>
    api.post('/process/steps', { has_minor_heir: hasMinor, has_dispute: hasDispute, is_selling: isSelling }),
  chat: (message, sessionId = null) => api.post('/chat/', { message, session_id: sessionId }),
  generateShareCertificate: (data) => api.post('/documents/share-certificate', data, { responseType: 'blob' }),
  generateLegalNotice: (data) => api.post('/documents/legal-notice', data, { responseType: 'blob' }),
  generateFIR: (data) => api.post('/documents/fir', data, { responseType: 'blob' }),
}