import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate, Navigate } from 'react-router-dom';
import axios from 'axios';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, PieChart, Pie, Cell, Legend
} from 'recharts';

import Login from './Login';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8001';

/* ---------------- ICONS ---------------- */
const Icons = {
  Home: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>,
  Stats: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>,
  User: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="7" r="4"/><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/></svg>,
  Plans: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>,
};

/* ---------------- DASHBOARD ---------------- */
function Dashboard() {
  const navigate = useNavigate();

  const [tab, setTab] = useState('Home');
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({
    faturamento: 0,
    comissao: 0,
    pedidosRecentes: [],
    pedidosPorStatus: {},
    faturamentoHistorico: [],
    statusChartData: []
  });

  const [motoristas, setMotoristas] = useState([]);
  const [showAddDriver, setShowAddDriver] = useState(false);

  const COLORS = ['#4c1d95', '#10b981', '#f59e0b', '#3b82f6', '#ef4444'];

  const getAuthHeader = () => {
    const token = localStorage.getItem('token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  const carregarDados = async () => {
    setLoading(true);
    try {
      const [pedidos, motos] = await Promise.all([
        axios.get(`${API_URL}/pedidos`, { headers: getAuthHeader() }),
        axios.get(`${API_URL}/motoristas`, { headers: getAuthHeader() })
      ]);

      const data = pedidos.data || [];

      const faturamento = data.reduce((a, p) => a + (Number(p.valor) || 0), 0);
      const comissao = data.reduce((a, p) => a + (Number(p.valor_comissao) || 0), 0);

      const porStatus = data.reduce((acc, p) => {
        acc[p.status] = (acc[p.status] || 0) + 1;
        return acc;
      }, {});

      const historico = Array.from({ length: 7 }).map((_, i) => ({
        name: `D${i + 1}`,
        valor: Math.floor(Math.random() * 500)
      }));

      setStats({
        faturamento,
        comissao,
        pedidosRecentes: data.slice(-5),
        pedidosPorStatus: porStatus,
        faturamentoHistorico: historico,
        statusChartData: Object.entries(porStatus).map(([name, value]) => ({ name, value }))
      });

      setMotoristas(motos.data || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    carregarDados();
  }, []);

  const ds = styles();

  return (
    <div style={ds.wrapper}>
      {/* SIDEBAR */}
      <aside style={ds.sidebar}>
        <div style={ds.logo}>🚐</div>

        <div onClick={() => setTab('Home')} style={tab === 'Home' ? ds.active : ds.item}><Icons.Home />Home</div>
        <div onClick={() => setTab('Stats')} style={tab === 'Stats' ? ds.active : ds.item}><Icons.Stats />Stats</div>
        <div onClick={() => setTab('User')} style={tab === 'User' ? ds.active : ds.item}><Icons.User />Frota</div>
        <div onClick={() => setTab('Plans')} style={tab === 'Plans' ? ds.active : ds.item}><Icons.Plans />Plans</div>

        <div onClick={() => navigate('/login')} style={ds.item}>Sair</div>
      </aside>

      {/* MAIN */}
      <main style={ds.main}>

        {/* HEADER */}
        <div style={ds.header}>
          <h2 style={ds.title}>Dashboard Central Transfers</h2>
          <button onClick={carregarDados} style={ds.refresh}>
            {loading ? '...' : '🔄'}
          </button>
        </div>

        {/* HOME */}
        {tab === 'Home' && (
          <div style={ds.grid}>
            <div style={ds.cardPurple}>
              <h3>Faturamento</h3>
              <h1>R$ {stats.faturamento.toLocaleString()}</h1>
            </div>

            <div style={ds.cardDark}>
              <h3>Motoristas</h3>
              <h1>{motoristas.length}</h1>
            </div>

            <div style={ds.cardWhite}>
              <h3 style={ds.darkText}>Últimos pedidos</h3>

              {stats.pedidosRecentes.map((p, i) => (
                <div key={i} style={ds.row}>
                  <div style={ds.statusIcon}>🚖</div>
                  <div>
                    <div style={ds.darkText}>{p.origem} → {p.destino}</div>
                    <small style={ds.muted}>{p.status}</small>
                  </div>
                  <strong style={ds.purple}>R$ {p.valor}</strong>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* STATS */}
        {tab === 'Stats' && (
          <div style={ds.grid}>
            <div style={ds.cardWhite}>
              <h3 style={ds.darkText}>Faturamento</h3>
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={stats.faturamentoHistorico}>
                  <Line dataKey="valor" stroke="#4c1d95" strokeWidth={3} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div style={ds.cardWhite}>
              <h3 style={ds.darkText}>Status</h3>

              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie data={stats.statusChartData} dataKey="value">
                    {stats.statusChartData.map((_, i) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
                    ))}
                  </Pie>
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {/* USERS */}
        {tab === 'User' && (
          <div style={ds.cardWhite}>
            <h2 style={ds.darkText}>Motoristas</h2>

            {motoristas.map((m, i) => (
              <div key={i} style={ds.row}>
                <div style={ds.avatar}>{m.nome?.[0]}</div>
                <div>
                  <div style={ds.darkText}>{m.nome}</div>
                  <small style={ds.muted}>{m.telefone}</small>
                </div>
              </div>
            ))}
          </div>
        )}

      </main>
    </div>
  );
}

/* ---------------- STYLES ---------------- */
const styles = () => ({
  wrapper: { display: 'flex', height: '100vh', fontFamily: 'Arial' },

  sidebar: {
    width: 90,
    background: '#fff',
    borderRight: '1px solid #eee',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    paddingTop: 20
  },

  logo: { fontSize: 22, marginBottom: 30 },

  item: {
    fontSize: 11,
    marginBottom: 20,
    cursor: 'pointer',
    color: '#666',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center'
  },

  active: {
    fontSize: 11,
    marginBottom: 20,
    cursor: 'pointer',
    color: '#4c1d95',
    fontWeight: 'bold',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center'
  },

  main: { flex: 1, padding: 30, background: '#f8fafc' },

  header: { display: 'flex', justifyContent: 'space-between' },

  title: { color: '#111' },

  refresh: { border: '1px solid #ddd', padding: 10, borderRadius: 10 },

  grid: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginTop: 20 },

  cardPurple: { background: '#4c1d95', color: '#fff', padding: 20, borderRadius: 20 },

  cardDark: { background: '#111827', color: '#fff', padding: 20, borderRadius: 20 },

  cardWhite: {
    background: '#fff',
    padding: 20,
    borderRadius: 20,
    border: '1px solid #eee'
  },

  row: {
    display: 'flex',
    justifyContent: 'space-between',
    padding: 10,
    borderBottom: '1px solid #eee'
  },

  statusIcon: { marginRight: 10 },

  darkText: { color: '#111827', fontWeight: 600 },

  muted: { color: '#6b7280', fontSize: 12 },

  purple: { color: '#4c1d95' },

  avatar: {
    width: 35,
    height: 35,
    borderRadius: 10,
    background: '#e5e7eb',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  }
});

/* ---------------- APP ---------------- */
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