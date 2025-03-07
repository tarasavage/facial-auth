import { Outlet } from 'react-router-dom';
import { AuthProvider } from '@/context/AuthContext';

export const RootLayout = () => {
  return (
    <AuthProvider>
      <Outlet />
    </AuthProvider>
  );
}; 