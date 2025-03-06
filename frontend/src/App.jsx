import { RouterProvider } from 'react-router-dom'
import { router } from '@/router/Routes.jsx'

import '@/styles/main.scss'

export const App = () => (
  <div className="app">
    <RouterProvider router={router} />
  </div>
)
