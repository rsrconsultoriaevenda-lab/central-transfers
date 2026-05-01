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
  Stats: () => <svg width="20" height="20" viewBox="0 0 24 24"><path d="M6 20V10M12 20V4M18 20V14"/></svg>,
  User: () => <svg width="20" height="20"><circle cx="12" cy="7" r="4"/></svg>,
  Settings: () => <svg width="20" height="20"><circle cx="12" cy="12" r="3"/></svg>
};

function Dashboard() {
  const navigate = useNavigate();

  const [tab, setTab] = useState('Home');
  const [loading, setLoading] = useState(false);
  const [showAddDriver, setShowAddDriver] = useState(false);

  const [stats, setStats] = useState({
    faturamento: 0,
    comissao: 0,
    totalBruto: 0,
    pedidosRecentes: [],
    totalMotoristas: 0,
    pedidosPorStatus: {},
    faturamentoHistorico: [],
    statusChartData: []
  });

  const [motoristas, setMotoristas] = useState([]);

  const COLORS = ['#4c1d95', '#10b981', '#f59e0b', '#3b82f6', '#ef4444'];

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
      const motoristasData = motoristasRes.data || [];

      const pedidosValidos = pedidos.filter(p =>
        ['PAGO', 'CONCLUIDO', 'ACEITO'].includes(p.status)
      );

      const faturamento = pedidosValidos.reduce(
        (acc, p) => acc + (Number(p.valor) || 0), 0
      );

      const comissao = pedidosValidos.reduce(
        (acc, p) => acc + (Number(p.valor_comissao) || 0), 0
      );

      const porStatus = pedidos.reduce((acc, p) => {
        acc[p.status] = (acc[p.status] || 0) + 1;
        return acc;
      }, {});

      const historico = Array.from({ length: 7 }, (_, i) => ({
        name: `D${i + 1}`,
        valor: Math.random() * 1000
      }));

      setMotoristas(motoristasData);

      setStats({
        faturamento,
        comissao,
        totalBruto: faturamento,
        pedidosRecentes: pedidos.slice(-5),
        totalMotoristas: motoristasData.length,
        pedidosPorStatus: porStatus,
        faturamentoHistorico: historico,
        statusChartData: Object.entries(porStatus).map(([name, value]) => ({
          name,
          value
        }))
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

  return (
    <div>
      <h1>Dashboard OK</h1>
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