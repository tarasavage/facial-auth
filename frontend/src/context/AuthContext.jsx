import { createContext, useState, useEffect } from "react";
import PropTypes from "prop-types";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(localStorage.getItem("token") || null);
  const [userInfo, setUserInfo] = useState(null);
  const backendUrl = import.meta.env.VITE_BACKEND_URL;

  const fetchUserInfo = async (accessToken) => {
    if (!accessToken) return;

    try {
      const response = await fetch(`${backendUrl}/registration/me`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to fetch user info");
      }

      const responseData = await response.json();
      setUserInfo({
        username: responseData.data.username,
        email: responseData.data.email,
        email_verified: responseData.data.email_verified,
      });
    } catch (error) {
      console.error("Error fetching user info:", error);
    }
  };

  const checkFaceAuth = async () => {
    try {
      const response = await fetch(`${backendUrl}/registration/check_face_auth`, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error("Failed to check face auth");
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error("Error checking face auth:", error);
      return false;
    }
  };

  const refreshToken = (newToken) => {
    setToken(newToken);
    localStorage.setItem("token", newToken);
    fetchUserInfo(newToken);
  };

  useEffect(() => {
    if (token) {
      fetchUserInfo(token);
    }
  }, [token]);

  const updateUserInfo = (newUserInfo, newToken) => {
    setUserInfo(newUserInfo);
    if (newToken) {
      setToken(newToken);
      localStorage.setItem("token", newToken);
    }
  };

  const logout = () => {
    localStorage.removeItem("token");
    setToken(null);
    setUserInfo(null);
    window.location.href = "/";
  };

  const login = async ({ email, password }) => {
    try {
      const response = await fetch(`${backendUrl}/registration/signin`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (response.ok) {
        refreshToken(data.access_token);
        return { success: true };
      }

      if (response.status === 403 && data.detail === "Email not verified") {
        return {
          success: false,
          message: `Email not verified. A verification email has been sent to ${data.email}.`,
          status: 403,
        };
      }

      return {
        success: false,
        message: data.detail,
        status: response.status,
      };
    } catch {
      return {
        success: false,
        message: "Login failed.",
        status: 500,
      };
    }
  };

  return (
    <AuthContext.Provider
      value={{ token, userInfo, login, updateUserInfo, refreshToken, logout, checkFaceAuth }}
    >
      {children}
    </AuthContext.Provider>
  );
};

AuthProvider.propTypes = {
  children: PropTypes.node.isRequired,
};
