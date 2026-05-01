import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate, Navigate } from 'react-router-dom';
import axios from 'axios';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend
} from 'recharts';

import Login from './Login';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8001';

const Icons = {
  Home: () => <svg width="20" height="20" viewBox="0 0 24 24"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>,
  Stats: () => <svg width="20" height="20" viewBox="0 0 24 24"><path d="M6 20v-6M12 20V4M18 20v-10"/></svg>,
  User: () => <svg width="20" height="20"><circle cx="12" cy="7" r="4"/><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/></svg>,
  Plans: () => <svg width="20" height="20"><rect x="2" y="7" width="20" height="14"/></svg>,
  Settings: () => <svg width="20" height="20"><circle cx="12" cy="12" r="3"/></svg>,
};

function Dashboard() {
  const navigate = useNavigate();

  const [tab, setTab] = useState('Home');
  const [loading, setLoading] = useState(false);
  const [showAddDriver, setShowAddDriver] = useState(false);

  const [stats, setStats] = useState({
    faturamento: 0,
    comissao: 0,
    pedidosRecentes: [],
    totalMotoristas: 0,
    pedidosPorStatus: {},
    faturamentoHistorico: [],
    statusChartData: []
  });

  const [motoristas, setMotoristas] = useState([]);

  const [adminInfo] = useState({
    name: "Renato Rocha",
    email: "renato@centraltransfers.com"
  });

  const COLORS = ['#4c1d95', '#10b981', '#f59e0b', '#3b82f6', '#ef4444'];

  const [newDriver, setNewDriver] = useState({
    nome: '',
    telefone: '',
    carro: '',
    placa: '',
    modelo: '',
    ano: new Date().getFullYear(),
    plano: 'MENSAL'
  });

  const getAuthHeader = () => {
    const token = localStorage.getItem('token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  const carregarDadosReais = async () => {
    setLoading(true);
    try {
      const [pedidosRes, motoristasRes] = await Promise.all([
        axios.get(`${API_URL}/pedidos`, { headers: getAuthHeader() }),
        axios.get(`${API_URL}/motoristas`, { headers: getAuthHeader() })
      ]);

      const pedidos = pedidosRes.data || [];

      const validos = pedidos.filter(p =>
        ['PAGO', 'CONCLUIDO', 'ACEITO'].includes(p.status)
      );

      const faturamento = validos.reduce((a, p) => a + (Number(p.valor) || 0), 0);
      const comissao = validos.reduce((a, p) => a + (Number(p.valor_comissao) || 0), 0);

      const porStatus = pedidos.reduce((acc, p) => {
        acc[p.status] = (acc[p.status] || 0) + 1;
        return acc;
      }, {});

      const hoje = new Date();

      const historico = Array.from({ length: 7 }).map((_, i) => {
        const d = new Date();
        d.setDate(hoje.getDate() - (6 - i));

        const iso = d.toISOString().split('T')[0];

        const totalDia = pedidos
          .filter(p => p.data_servico?.startsWith(iso))
          .reduce((a, p) => a + (Number(p.valor) || 0), 0);

        return {
          name: d.toLocaleDateString('pt-BR', { weekday: 'short' }),
          valor: totalDia
        };
      });

      setMotoristas(motoristasRes.data || []);

      setStats({
        faturamento,
        comissao,
        pedidosRecentes: pedidos.slice(-5).reverse(),
        totalMotoristas: motoristasRes.data?.length || 0,
        pedidosPorStatus: porStatus,
        faturamentoHistorico: historico,
        statusChartData: Object.entries(porStatus).map(([name, value]) => ({ name, value }))
      });

    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    carregarDadosReais();
  }, []);

  const ds = {
    wrapper: { display: 'flex', height: '100vh', fontFamily: 'Inter' },
    sidebar: { width: 90, background: '#fff', padding: 20 },
    main: { flex: 1, padding: 30, overflowY: 'auto' },
    card: { background: '#fff', padding: 20, borderRadius: 20 }
  };

  return (
    <div style={ds.wrapper}>
      <aside style={ds.sidebar}>
        <div onClick={() => setTab('Home')}>🏠</div>
        <div onClick={() => setTab('Stats')}>📊</div>
        <div onClick={() => setTab('User')}>👤</div>
        <div onClick={() => setTab('Plans')}>💳</div>
        <div onClick={() => navigate('/login')}>🚪</div>
      </aside>

      <main style={ds.main}>
        <h2>Olá {adminInfo.name}</h2>

        {tab === 'Home' && (
          <div style={ds.card}>
            <h3>Faturamento: R$ {stats.faturamento.toLocaleString()}</h3>

            <h4>Últimos pedidos</h4>
            {stats.pedidosRecentes.map(p => (
              <div key={p.id}>
                {p.origem} → {p.destino} | R$ {p.valor}
              </div>
            ))}
          </div>
        )}

        {tab === 'Stats' && (
          <div style={ds.card}>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={stats.faturamentoHistorico}>
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Line dataKey="valor" stroke="#4c1d95" />
              </LineChart>
            </ResponsiveContainer>

            <PieChart width={300} height={300}>
              <Pie data={stats.statusChartData} dataKey="value">
                {stats.statusChartData.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Legend />
            </PieChart>
          </div>
        )}
      </main>
    </div>
  );
}

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/" element={<Navigate to="/login" />} />
      </Routes>
    </Router>
  );
}