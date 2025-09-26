// src/contexts/AuthContext.jsx
import React, { createContext, useContext, useState, useEffect } from "react";
import axios from "axios";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const apiUrl = import.meta.env.VITE_API_URL;

  // Obter usuário atual
  const getCurrentUser = async (accessToken) => {
    try {
      const res = await axios.get(`${apiUrl}/auth/me`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      setUser(res.data);
      return { success: true, user: res.data };
    } catch (err) {
      console.error("Failed to load user:", err);
      setUser(null);
      return { success: false, error: err.response?.data?.detail || err.message };
    }
  };

  // Login
  const login = async (email, password) => {
    try {
      const res = await axios.post(`${apiUrl}/auth/login`, { email, password });
      const { access_token, refresh_token } = res.data;

      localStorage.setItem("access_token", access_token);
      localStorage.setItem("refresh_token", refresh_token);

      // Busca dados completos do usuário usando o token correto
      return await getCurrentUser(access_token);
    } catch (err) {
      console.error("Login failed:", err);
      const message = err.response?.data?.detail || "Erro de conexão ou credenciais inválidas";
      return { success: false, error: message };
    }
  };

  // Registro
  const register = async (full_name, email, password) => {
    try {
      const res = await axios.post(`${apiUrl}/auth/register`, {
        full_name,
        email,
        password,
      });

      if (res.status === 200 || res.status === 201) {
        return { success: true };
      }

      return { success: false, error: "Erro no cadastro" };
    } catch (err) {
      console.error("Register failed:", err);
      const message = err.response?.data?.detail || "Erro de conexão com o servidor";
      return { success: false, error: message };
    }
  };

  // Logout
  const logout = () => {
    setUser(null);
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  };

  // Carrega usuário atual ao iniciar app se houver token
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      getCurrentUser(token);
    }
  }, []);

  return (
    <AuthContext.Provider value={{ user, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
