import { createBrowserRouter } from 'react-router-dom';
import { HomePage } from '../pages/HomePage';
import { ConfirmSignup } from '../pages/auth/ConfirmSignup';
import { SignUp } from '../pages/auth/SignUp';
import { Signin } from '../pages/auth/Signin';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <HomePage />,
  },
  {
    path: '/signup',
    element: <SignUp />,
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