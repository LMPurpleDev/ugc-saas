import React, { createContext, useState, useEffect, useContext } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadUser = async () => {
      try {
        const token = localStorage.getItem('accessToken');
        if (token) {
          axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          const response = await axios.get(`${import.meta.env.VITE_API_URL}/users/me`);
          setUser(response.data);
        }
      } catch (error) {
        console.error('Failed to load user:', error);
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    loadUser();
  }, []);

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${import.meta.env.VITE_API_URL}/auth/login`, { email, password });
      const { access_token, refresh_token } = response.data;
      localStorage.setItem("accessToken", access_token);
      localStorage.setItem("refreshToken", refresh_token);
      axios.defaults.headers.common["Authorization"] = `Bearer ${access_token}`;
      const userResponse = await axios.get(`${import.meta.env.VITE_API_URL}/users/me`);
      setUser(userResponse.data);
      return { success: true };
    } catch (error) {
      console.error("Login failed:", error);
      return { success: false, error: error.response?.data?.detail || "Erro ao fazer login" };
    }
  };

  const register = async (full_name, email, password) => {
    try {
      const response = await axios.post(`${import.meta.env.VITE_API_URL}/auth/register`, { full_name, email, password });
      return { success: true, data: response.data };
    } catch (error) {
      console.error("Registration failed:", error);
      return { success: false, error: error.response?.data?.detail || "Erro ao registrar" };
    }
  };

  const logout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);


