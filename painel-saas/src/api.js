const API = import.meta.env.VITE_API_URL;

let token = localStorage.getItem("token") || null;

export const setToken = (newToken) => {
  token = newToken;
  localStorage.setItem("token", newToken);
};

const request = async (endpoint, options = {}) => {
  const headers = options.headers || {};

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    throw new Error("Erro na requisição");
  }

  return response.json();
};

export default {
  request,
  setToken,
};