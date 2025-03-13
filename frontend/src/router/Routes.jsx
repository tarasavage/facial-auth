import {
  createBrowserRouter,
  createRoutesFromElements,
  Route,
} from "react-router-dom";

import { HomePage } from "@/pages/HomePage";
import { ConfirmSignup } from "@/pages/auth/ConfirmSignup";
import { Signup } from "@/pages/auth/Signup";
import { Signin } from "@/pages/auth/Signin";
import { FaceRegistration } from "@/pages/auth/FaceRegistration";
import { ProtectedLayout } from "@/router/ProtectedLayout";
import { ProtectedRoute } from "@/router/ProtectedRoute";
import { ProfilePage } from "@/pages/auth/ProfilePage";
import { RootLayout } from "@/router/RootLayout";

export const router = createBrowserRouter(
  createRoutesFromElements(
    <Route element={<RootLayout />}>
      <Route path="/" element={<HomePage />} />
      <Route path="/signup" element={<Signup />} />
      <Route path="/confirm-signup" element={<ConfirmSignup />} />
      <Route path="/signin" element={<Signin />} />

      {/* Protected routes */}
      <Route path="/" element={<ProtectedLayout />}>
        <Route
          path="/me"
          element={
            <ProtectedRoute>
              <ProfilePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/register-face"
          element={
            <ProtectedRoute>
              <FaceRegistration />
            </ProtectedRoute>
          }
        />
      </Route>
    </Route>,
  ),
);
