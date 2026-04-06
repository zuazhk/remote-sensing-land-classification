import axios from "axios";
import { API_BASE_URL, API_ENDPOINTS } from "../config/api";

// Local token storage key
const TOKEN_KEY = "token";

// Simple token helpers
export const setToken = (token: string) => {
  localStorage.setItem(TOKEN_KEY, token);
};

export const getToken = (): string | null => {
  return localStorage.getItem(TOKEN_KEY);
};

export const removeToken = () => {
  localStorage.removeItem(TOKEN_KEY);
};

// Axios instance with base URL
const api = axios.create({
  baseURL: API_BASE_URL,
});

// Request interceptor to attach token
api.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token && config.headers) {
      // Ensure we don't overwrite existing Authorization headers
      config.headers["Authorization"] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status;
    if (status === 401) {
      // Invalidate token and redirect to login
      removeToken();
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default api;
