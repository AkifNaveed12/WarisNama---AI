// import React from 'react'

// const Button = ({ children, onClick, type = 'button', variant = 'primary', loading = false, disabled = false, className = '' }) => {
//   const base = 'px-4 py-2 rounded-md font-medium focus:outline-none transition duration-200'
//   const variants = {
//     primary: 'bg-blue-600 text-white hover:bg-blue-700 disabled:bg-blue-300',
//     secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300 disabled:bg-gray-100',
//     danger: 'bg-red-600 text-white hover:bg-red-700 disabled:bg-red-300',
//   }
//   return (
//     <button
//       type={type}
//       onClick={onClick}
//       disabled={disabled || loading}
//       className={`${base} ${variants[variant]} ${className}`}
//     >
//       {loading ? 'Loading...' : children}
//     </button>
//   )
// }

// export default Button




import React from 'react'
import { Loader2 } from 'lucide-react'

const Button = ({ children, onClick, type = 'button', variant = 'primary', loading = false, disabled = false, className = '' }) => {
  const base = 'inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed'
  const variants = {
    primary: 'bg-gradient-to-r from-blue-700 to-blue-600 text-white hover:from-blue-800 hover:to-blue-700 shadow-md hover:shadow-lg focus:ring-blue-500',
    secondary: 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50 hover:border-gray-400 focus:ring-gray-500',
    danger: 'bg-gradient-to-r from-red-600 to-red-500 text-white hover:from-red-700 hover:to-red-600 shadow-md focus:ring-red-500',
    success: 'bg-gradient-to-r from-green-600 to-green-500 text-white hover:from-green-700 hover:to-green-600 shadow-md focus:ring-green-500',
    outline: 'border-2 border-blue-600 text-blue-600 hover:bg-blue-50 focus:ring-blue-500',
  }
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={`${base} ${variants[variant]} ${className}`}
    >
      {loading && <Loader2 className="w-4 h-4 animate-spin" />}
      {children}
    </button>
  )
}

export default Button