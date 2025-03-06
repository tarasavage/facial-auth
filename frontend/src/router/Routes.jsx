import { createBrowserRouter } from 'react-router-dom';

import { HomePage } from '@/pages/HomePage';
import { ConfirmSignup } from '@/pages/auth/ConfirmSignup';
import { Signup } from '@/pages/auth/Signup';
import { Signin } from '@/pages/auth/Signin';
import { FaceRegistration } from '@/pages/auth/FaceRegistration';


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
  {
    path: '/face-registration',
    element: <FaceRegistration />,
  },
]);