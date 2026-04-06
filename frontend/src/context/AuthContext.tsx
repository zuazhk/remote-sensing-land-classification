import React, { createContext, useContext, useEffect, useState } from "react";
import api from "../api/client";
import { API_ENDPOINTS } from "../config/api";
import { getToken, removeToken, setToken } from "../api/client";

type User = { id: number; username: string; email?: string } | null;

type AuthContextType = {
  user: User;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  register: (username: string, email: string, password: string) => Promise<void>;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = (): AuthContextType => {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return ctx;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);

  // Attempt to validate existing token on mount
  useEffect(() => {
    const token = getToken();
    if (token) {
      // Try to access a protected endpoint to validate token
      api
        .get(API_ENDPOINTS.history)
        .then(() => {
          setIsAuthenticated(true);
          // Best-effort: show username if previously stored, otherwise fallback
          const storedName = localStorage.getItem("username");
          setUser(storedName ? { id: -1, username: storedName } : { id: -1, username: "User" });
        })
        .catch(() => {
          // Token invalid or expired
          removeToken();
          localStorage.removeItem("username");
          setIsAuthenticated(false);
          setUser(null);
        });
    }
  }, []);

  const login = async (username: string, password: string) => {
    // Call login endpoint and store token
    const res = await api.post(API_ENDPOINTS.auth.login, { username, password });
    const token = (res.data?.access_token ?? res.data?.token) as string | undefined;
    if (!token) {
      throw new Error("Invalid credentials");
    }
    setToken(token);
    localStorage.setItem("username", username);
    setUser({ id: Date.now(), username, email: "" });
    setIsAuthenticated(true);
  };

  const register = async (username: string, email: string, password: string) => {
    // Register user; backend returns user info on success.
    const res = await api.post(API_ENDPOINTS.auth.register, {
      username,
      email,
      password,
    });
    // If backend returns a user, we could auto-login, but keep UI simple: rely on login page
    // so just resolve successfully
    return;
  };

  const logout = () => {
    removeToken();
    localStorage.removeItem("username");
    setUser(null);
    setIsAuthenticated(false);
    // Redirect to home
    window.location.assign("/");
  };

  const value: AuthContextType = {
    user,
    isAuthenticated,
    login,
    logout,
    register,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext;
