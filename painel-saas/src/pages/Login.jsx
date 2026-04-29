import React, { useState } from 'react';
import api from '../services/api';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    try {
      const response = await fetch('https://central-transfers-backend-production.up.railway.app', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) throw new Error('Credenciais inválidas');
      
      const data = await response.json();
      api.setToken(data.access_token);
      window.location.href = '/';
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-100 font-sans">
      <div className="bg-white p-10 rounded-3xl shadow-xl w-full max-w-md border border-slate-200">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-slate-900">Central Transfers</h1>
          <p className="text-slate-500 mt-2">Acesse seu painel administrativo</p>
        </div>
        <form onSubmit={handleLogin} className="space-y-6">
          {error && <p className="text-red-500 text-sm bg-red-50 p-3 rounded-lg border border-red-100">{error}</p>}
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-2">Usuário</label>
            <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} className="w-full p-4 rounded-xl border border-slate-200 focus:ring-2 focus:ring-indigo-500 transition-all outline-none" required />
          </div>
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-2">Senha</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="w-full p-4 rounded-xl border border-slate-200 focus:ring-2 focus:ring-indigo-500 transition-all outline-none" required />
          </div>
          <button type="submit" className="w-full bg-indigo-600 hover:bg-indigo-700 text-white p-4 rounded-xl font-bold shadow-lg shadow-indigo-200 transition-all active:scale-[0.98]">Entrar</button>
        </form>
      </div>
    </div>
  );
};

export default Login;