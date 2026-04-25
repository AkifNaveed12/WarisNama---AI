import React from 'react'

const Button = ({ children, onClick, type = 'button', variant = 'primary', loading = false, disabled = false, className = '' }) => {
  const base = 'px-4 py-2 rounded-md font-medium focus:outline-none transition duration-200'
  const variants = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 disabled:bg-blue-300',
    secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300 disabled:bg-gray-100',
    danger: 'bg-red-600 text-white hover:bg-red-700 disabled:bg-red-300',
  }
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={`${base} ${variants[variant]} ${className}`}
    >
      {loading ? 'Loading...' : children}
    </button>
  )
}

export default Button