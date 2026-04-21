import React, { useEffect, useState } from 'react';
import api from '../services/api';

const Dashboard = () => {
  const [stats, setStats] = useState({
    total_pedidos: 0,
    pendentes: 0,
    aguardando_pagamento: 0,
    pagos: 0,
    aceitos: 0,
    concluidos: 0,
    faturamento_total: 0
  });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await api.get('/pedidos/stats');
        const data = await response.json();
        setStats(data);
      } catch (error) {
        console.error("Erro ao buscar estatísticas:", error);
      }
    };
    fetchStats();
  }, []);

  return (
    <div className="p-8 bg-slate-50 min-h-screen font-sans">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-10">
          <div>
            <h1 className="text-4xl font-extrabold text-slate-900 tracking-tight">Dashboard Central</h1>
            <p className="text-slate-500 mt-2">Gestão de frotas e transferências em tempo real.</p>
          </div>
          <button className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-xl font-semibold shadow-lg shadow-indigo-200 transition-all active:scale-95">
            + Novo Serviço Manual
          </button>
        </div>

        {/* Cards de Métricas Principais */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <MetricCard title="Faturamento Bruto" value={`R$ ${stats.faturamento_total}`} icon="💰" color="bg-emerald-500" />
          <MetricCard title="Pedidos Confirmados" value={stats.pagos} icon="✅" color="bg-blue-500" />
          <MetricCard title="Aguardando Pix" value={stats.aguardando_pagamento} icon="⏳" color="bg-amber-500" />
          <MetricCard title="Viagens Concluídas" value={stats.concluidos} icon="🏁" color="bg-slate-700" />
        </div>

        {/* Barra de Progresso da Operação */}
        <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200">
          <h2 className="text-lg font-bold text-slate-800 mb-6">Status dos Pedidos Ativos</h2>
          <div className="flex items-center justify-between gap-6">
            <StatusBar label="Pendentes" count={stats.pendentes} color="bg-slate-200" />
            <StatusBar label="Em Pagamento" count={stats.aguardando_pagamento} color="bg-amber-200" />
            <StatusBar label="Pagos" count={stats.pagos} color="bg-blue-200" />
            <StatusBar label="Em Viagem" count={stats.aceitos} color="bg-indigo-200" />
          </div>
        </div>
      </div>
    </div>
  );
};

const MetricCard = ({ title, value, icon, color }) => (
  <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex items-center gap-4 hover:shadow-md transition-shadow">
    <div className={`${color} w-12 h-12 rounded-full flex items-center justify-center text-xl text-white shadow-inner`}>{icon}</div>
    <div>
      <p className="text-sm font-medium text-slate-500 uppercase tracking-wider">{title}</p>
      <p className="text-2xl font-bold text-slate-900">{value}</p>
    </div>
  </div>
);

const StatusBar = ({ label, count, color }) => (
  <div className="flex-1 text-center">
    <div className={`h-4 rounded-full ${color} mb-3 w-full overflow-hidden`}>
      <div className="h-full bg-black/5 animate-pulse"></div>
    </div>
    <p className="text-xs font-bold text-slate-700 uppercase">{label}</p>
    <p className="text-sm text-slate-500 font-medium">{count} registros</p>
  </div>
);

export default Dashboard;