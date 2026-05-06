const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8001';

const api = {
  getToken: () => localStorage.getItem('token'),

  setToken: (token) => localStorage.setItem('token', token),

  logout: () => {
    localStorage.removeItem('token');
    window.location.href = '/login';
  },

  async request(endpoint, options = {}) {
    const token = this.getToken();

    const headers = {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    let response;

    try {
      response = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        headers,
      });
    } catch (err) {
      console.error('Erro de rede:', err);
      throw new Error('Erro de conexão com o servidor');
    }

    // 🔒 AUTO LOGOUT (token inválido ou expirado)
    if (response.status === 401) {
      this.logout();
      return;
    }

    // 🔥 tenta parsear JSON com segurança
    let data = null;
    const contentType = response.headers.get('content-type');

    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    } else {
      data = await response.text();
    }

    // 🔥 erro HTTP tratado corretamente
    if (!response.ok) {
      const message =
        data?.detail ||
        data?.message ||
        'Erro inesperado na requisição';

      throw new Error(message);
    }

    return data;
  },

  get: (endpoint) => api.request(endpoint, { method: 'GET' }),

  post: (endpoint, body) =>
    api.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  put: (endpoint, body) =>
    api.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(body),
    }),

  delete: (endpoint) =>
    api.request(endpoint, { method: 'DELETE' }),
};

export default api;