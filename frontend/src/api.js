import axios from 'axios';

const isDevelopment = import.meta.env.MODE === 'development';

const api = axios.create({
  // No dev, usa o proxy local '/api'. No prod, usa a URL oficial ou o rewrite do Vercel
  baseURL: isDevelopment ? '/api' : (import.meta.env.VITE_API_URL || ''),
  withCredentials: true, 
  headers: {
    'Content-Type': 'application/json'
  }
});

// Interceptor para anexar o Token JWT automaticamente em todas as chamadas
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para tratamento global de erros
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.response?.data?.message || error.message;
    console.error(`[API Error - ${error.config?.url}]:`, message);
    return Promise.reject(error);
  }
);

// Apenas UM export default por arquivo
export default api;