import { createBrowserRouter } from 'react-router-dom';

import { HomePage } from '@/pages/HomePage';
import { ConfirmSignup } from '@/pages/auth/ConfirmSignup';
import { Signup } from '@/pages/auth/Signup';
import { Signin } from '@/pages/auth/Signin';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <HomePage />,
  },
  {
    path: '/signup',
    element: <Signup />,
  },
  {
    path: '/confirm-signup',
    element: <ConfirmSignup />,
  },
  {
    path: '/signin',
    element: <Signin />,
  },
]);