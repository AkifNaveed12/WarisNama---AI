// import React from 'react'
// import { NavLink } from 'react-router-dom'

// const Sidebar = () => {
//   const navItems = [
//     { name: 'Calculator', path: '/', icon: '🧮' },
//     { name: 'Chatbot', path: '/chat', icon: '💬' },
//   ]

//   return (
//     <aside className="w-64 bg-white shadow-md flex flex-col">
//       <div className="p-4 border-b">
//         <h1 className="text-xl font-bold text-blue-600">WarisNama AI</h1>
//       </div>
//       <nav className="flex-1 p-4">
//         <ul className="space-y-2">
//           {navItems.map((item) => (
//             <li key={item.path}>
//               <NavLink
//                 to={item.path}
//                 className={({ isActive }) =>
//                   `flex items-center space-x-3 px-4 py-2 rounded-md transition ${
//                     isActive ? 'bg-blue-100 text-blue-700' : 'text-gray-700 hover:bg-gray-100'
//                   }`
//                 }
//               >
//                 <span>{item.icon}</span>
//                 <span>{item.name}</span>
//               </NavLink>
//             </li>
//           ))}
//         </ul>
//       </nav>
//     </aside>
//   )
// }

// export default Sidebar

import React from 'react'
import { NavLink } from 'react-router-dom'
import { Calculator, MessageSquare } from 'lucide-react'

const Sidebar = () => {
  const navItems = [
    { name: 'Calculator', path: '/', icon: Calculator },
    { name: 'Chatbot', path: '/chat', icon: MessageSquare },
  ]

  return (
    <aside className="w-64 bg-white shadow-xl flex flex-col z-10">
      <div className="p-5 border-b border-gray-100">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-700 to-blue-500 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-lg">و</span>
          </div>
          <h1 className="text-xl font-bold bg-gradient-to-r from-blue-700 to-blue-500 bg-clip-text text-transparent">
            WarisNama AI
          </h1>
        </div>
        <p className="text-xs text-gray-500 mt-1">Inheritance Resolution</p>
      </div>
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon
            return (
              <li key={item.path}>
                <NavLink
                  to={item.path}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 ${
                      isActive
                        ? 'bg-gradient-to-r from-blue-50 to-indigo-50 text-blue-700 shadow-sm border-r-4 border-blue-600'
                        : 'text-gray-600 hover:bg-gray-50 hover:text-blue-600'
                    }`
                  }
                >
                  <Icon size={20} />
                  <span className="font-medium">{item.name}</span>
                </NavLink>
              </li>
            )
          })}
        </ul>
      </nav>
      <div className="p-4 border-t border-gray-100">
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-3 text-center">
          <p className="text-xs text-gray-500">Powered by</p>
          <p className="text-sm font-semibold text-blue-800">WarisNama AI</p>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar