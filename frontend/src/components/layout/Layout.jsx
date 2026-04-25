// import React from 'react'
// import Sidebar from './Sidebar'

// const Layout = ({ children }) => {
//   return (
//     <div className="flex h-screen bg-gray-100">
//       <Sidebar />
//       <main className="flex-1 overflow-auto p-6">{children}</main>
//     </div>
//   )
// }

// export default Layout



import React from 'react'
import Sidebar from './Sidebar'

const Layout = ({ children }) => {
  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar />
      <main className="flex-1 overflow-auto p-6 animate-fadeIn">
        <div className="max-w-7xl mx-auto">
          {children}
        </div>
      </main>
    </div>
  )
}

export default Layout