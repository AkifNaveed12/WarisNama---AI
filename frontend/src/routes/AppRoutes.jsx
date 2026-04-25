import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Layout from '../components/layout/Layout'
import CalculatorPage from '../features/calculator/pages/CalculatorPage'
import ChatbotPage from '../features/chatbot/pages/ChatbotPage'
import NotFound from '../pages/NotFound'

const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/" element={<Layout><CalculatorPage /></Layout>} />
      <Route path="/chat" element={<Layout><ChatbotPage /></Layout>} />
      <Route path="*" element={<Layout><NotFound /></Layout>} />
    </Routes>
  )
}

export default AppRoutes