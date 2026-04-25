// import React from 'react'

// const Input = ({ label, name, type = 'text', value, onChange, error, required = false, placeholder = '', className = '' }) => {
//   return (
//     <div className={`mb-4 ${className}`}>
//       {label && (
//         <label htmlFor={name} className="block text-sm font-medium text-gray-700 mb-1">
//           {label} {required && <span className="text-red-500">*</span>}
//         </label>
//       )}
//       <input
//         id={name}
//         name={name}
//         type={type}
//         value={value}
//         onChange={onChange}
//         placeholder={placeholder}
//         className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${error ? 'border-red-500' : 'border-gray-300'}`}
//       />
//       {error && <p className="mt-1 text-sm text-red-500">{error}</p>}
//     </div>
//   )
// }

// export default Input





import React, { useState } from 'react'

const Input = ({ label, name, type = 'text', value, onChange, error, required = false, placeholder = '', className = '' }) => {
  const [isFocused, setIsFocused] = useState(false)
  const hasValue = value !== '' && value !== undefined && value !== null

  return (
    <div className={`relative mb-4 ${className}`}>
      <input
        id={name}
        name={name}
        type={type}
        value={value}
        onChange={onChange}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        placeholder={placeholder || ' '}
        className={`peer w-full px-4 py-3 rounded-xl border-2 bg-white/50 backdrop-blur-sm transition-all duration-200 focus:outline-none focus:ring-0 ${
          error ? 'border-red-500 focus:border-red-500' : 'border-gray-200 focus:border-blue-500'
        }`}
      />
      <label
        htmlFor={name}
        className={`absolute left-4 transition-all duration-200 pointer-events-none ${
          isFocused || hasValue
            ? '-top-2.5 text-xs font-medium bg-white px-1 text-blue-600'
            : 'top-3.5 text-gray-500'
        }`}
      >
        {label} {required && <span className="text-red-500">*</span>}
      </label>
      {error && <p className="mt-1 text-sm text-red-500">{error}</p>}
    </div>
  )
}

export default Input