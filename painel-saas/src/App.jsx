﻿import React, { useState, useEffect } from 'react';
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
import DriverApp from './DriverApp';
import Storefront from './Storefront';
import Success from '../../../Success';
import Failure from '../../../Failure';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8001';

// Cores do Sistema - Facilita a troca de tema (Branding)
const THEME = {
  primary: '#4c1d95',
  secondary: '#7c3aed',
  success: '#10b981',
  warning: '#f59e0b',
  danger: '#ef4444',
  textMain: '#0F172A',
  textLight: '#94A3B8'
};

const ProtectedRoute = ({ children, allowedRoles }) => {
  // SEGURANÇA DESABILITADA: Permite acesso direto a qualquer rota sem validar token ou papel
  // Permite acesso direto a qualquer rota
  return children;
};

const Icons = {
  Home: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>,
  Stats: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M6 20V10M12 20V4M18 20V14"/></svg>,
  User: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="7" r="4"/><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/></svg>,
  Catalog: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82zM6.5 8.5a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3z"/></svg>,
  Settings: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>,
  Live: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>
};

function Dashboard() {
  const navigate = useNavigate();

  const [tab, setTab] = useState('Home');
  const [loading, setLoading] = useState(false);
  const [showAddDriver, setShowAddDriver] = useState(false);
  const [showAddService, setShowAddService] = useState(false);
  const [showSuccessAnimation, setShowSuccessAnimation] = useState(false);
  const [qrModal, setQrModal] = useState({ open: false, link: '', title: '' });

  const [stats, setStats] = useState({
    faturamento: 0,
    comissao: 0,
    totalBruto: 0,
    pedidosRecentes: [],
    totalMotoristas: 0,
    pedidosPorStatus: {},
    faturamentoHistorico: [],
    statusChartData: [],
    novosPedidosCount: 0,
    servicosPendentesCount: 0
  });

  const [motoristas, setMotoristas] = useState([]);
  const [servicos, setServicos] = useState([]);
  const [driverStatusFilter, setDriverStatusFilter] = useState('ALL'); // Novo estado para o filtro de status
  const [driverFilter, setDriverFilter] = useState('ALL');

  const adminInfo = { name: "Renato Rocha", email: "renato@centraltransfers.com" };
  const COLORS = ['#4c1d95', '#10b981', '#f59e0b', '#3b82f6', '#ef4444'];

  const abrirGeradorQR = (codigo, nome) => {
    // Gera a URL de indicação baseada no domínio atual
    const baseUrl = window.location.origin + "/store";
    const referralLink = `${baseUrl}?ref=${codigo}`;
    setQrModal({ open: true, link: referralLink, title: nome });
  };

  const [newDriver, setNewDriver] = useState({
    nome: '', telefone: '', carro: '', placa: '', modelo: '', ano: new Date().getFullYear(), plano: 'MENSAL'
  });

  const [newService, setNewService] = useState({
    nome: '', categoria: 'TRANSFERS', valor: '', descricao: '', imagem: null
  });

  const getAuthHeader = () => {
    const token = localStorage.getItem('token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  const carregarDadosReais = async () => {
    setLoading(true);
    try {
      const [pedidosRes, motoristasRes, servicosRes] = await Promise.all([
        axios.get(`${API_URL}/pedidos`, { headers: getAuthHeader() }),
        axios.get(`${API_URL}/motoristas`, { headers: getAuthHeader() }),
        axios.get(`${API_URL}/servicos`, { headers: getAuthHeader() })
      ]);

      const pedidos = pedidosRes.data || [];
      const motoristasData = motoristasRes.data || [];
      const servicosData = servicosRes.data || [];

      const pedidosValidos = pedidos.filter(p => ['PAGO', 'CONCLUIDO', 'ACEITO'].includes(p.status));
      const faturamento = pedidosValidos.reduce((acc, p) => acc + (parseFloat(p.valor) || 0), 0);
      const comissao = pedidosValidos.reduce((acc, p) => acc + (parseFloat(p.valor_comissao) || 0), 0);

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
          .filter(p => p.data_servico?.startsWith(iso) && ['PAGO', 'CONCLUIDO', 'ACEITO'].includes(p.status))
          .reduce((acc, p) => acc + (parseFloat(p.valor) || 0), 0);
        return { name: d.toLocaleDateString('pt-BR', { weekday: 'short' }), valor: totalDia };
      });

      setMotoristas(motoristasData);
      setServicos(servicosData);

      setStats({
        faturamento,
        comissao,
        totalBruto: faturamento,
        pedidosRecentes: [...pedidos].reverse().slice(0, 5),
        totalMotoristas: motoristasData.length,
        pedidosPorStatus: porStatus,
        faturamentoHistorico: historico,
        statusChartData: Object.entries(porStatus).map(([name, value]) => ({ name, value })),
        novosPedidosCount: (porStatus['PENDENTE'] || 0) + (porStatus['AGUARDANDO_PAGAMENTO'] || 0),
        servicosPendentesCount: porStatus['ACEITO'] || 0
      });

    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const alterarPlanoMotorista = async (id, planoAtual) => {
    const novoPlano = planoAtual === 'MASTER' ? 'MENSAL' : 'MASTER';
    if (!window.confirm(`Deseja alterar o plano para ${novoPlano}?`)) return;
    try {
      setLoading(true);
      await axios.patch(`${API_URL}/motoristas/${id}`, { plano: novoPlano }, { headers: getAuthHeader() });
      await carregarDadosReais();
    } catch (err) { alert("Erro ao atualizar plano."); }
    finally { setLoading(false); }
  };

  const handleStatusMotorista = async (id, novoStatus) => {
    const acao = novoStatus === 'ATIVO' ? 'aprovar' : 'rejeitar';
    if (!window.confirm(`Deseja realmente ${acao} este cadastro?`)) return;
    try {
      setLoading(true);
      await axios.patch(`${API_URL}/motoristas/${id}/status`, { status: novoStatus }, { headers: getAuthHeader() });
      await carregarDadosReais();
    } catch (err) { 
      alert("Erro ao atualizar status do motorista."); 
    } finally { setLoading(false); }
  };

  const cadastrarMotorista = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await axios.post(`${API_URL}/motoristas`, newDriver, { headers: getAuthHeader() });
      
      const { acesso } = res.data;
      if (acesso && acesso.senha) {
        alert(`✅ Motorista Cadastrado!\n\nLOGIN: ${acesso.login}\nSENHA TEMPORÁRIA: ${acesso.senha}\n\nAnote estes dados para passar ao motorista.`);
      }

      setShowAddDriver(false);
      setNewDriver({ nome: '', telefone: '', carro: '', placa: '', modelo: '', ano: new Date().getFullYear(), plano: 'MENSAL' });
      await carregarDadosReais();
      setShowSuccessAnimation(true); // Mostrar animação de sucesso
      setTimeout(() => setShowSuccessAnimation(false), 2000); // Esconder após 2 segundos
    } catch (err) { 
      console.error("Erro ao cadastrar motorista:", err.response?.data || err.message); 
      alert(`Erro ao cadastrar motorista: ${JSON.stringify(err.response?.data?.detail || "Erro interno")}`); 
    }
    finally { setLoading(false); }
  };

  const cadastrarServico = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    const formData = new FormData();
    formData.append('nome', newService.nome);
    formData.append('categoria', newService.categoria);
    formData.append('valor', parseFloat(newService.valor) || 0);
    formData.append('descricao', newService.descricao);
    if (newService.imagem) formData.append('imagem', newService.imagem);

    try {
      await axios.post(`${API_URL}/servicos`, formData, { 
        headers: { ...getAuthHeader(), 'Content-Type': 'multipart/form-data' } 
      });
      setShowAddService(false);
      setNewService({ nome: '', categoria: 'TRANSFERS', valor: '', descricao: '', imagem: null });
      await carregarDadosReais();
      setShowSuccessAnimation(true);
      setTimeout(() => setShowSuccessAnimation(false), 2000);
    } catch (err) { 
      console.error("Erro ao cadastrar serviço:", err.response?.data || err.message); 
      alert(`Erro ao cadastrar serviço: ${JSON.stringify(err.response?.data?.detail || "Verifique se as colunas categoria/valor existem no banco.")}`); 
    }
    finally { setLoading(false); }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  useEffect(() => {
    carregarDadosReais();
    // Atualização automática a cada 30 segundos para garantir tempo real
    const interval = setInterval(carregarDadosReais, 30000);
    
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={ds.wrapper}>
      <aside style={ds.sidebar}>
        <div style={{fontSize: '24px', marginBottom: '30px'}}>🚐</div>
        <div onClick={() => setTab('Home')} style={tab === 'Home' ? ds.sideIconActive : ds.sideIcon}><Icons.Home /><span style={ds.sideLabel}>HOME</span></div>
        <div onClick={() => setTab('Stats')} style={tab === 'Stats' ? ds.sideIconActive : ds.sideIcon}><Icons.Stats /><span style={ds.sideLabel}>STAT</span></div>
        <div onClick={() => setTab('Live')} style={tab === 'Live' ? ds.sideIconActive : ds.sideIcon}><Icons.Live /><span style={ds.sideLabel}>LIVE</span></div>
        <div onClick={() => setTab('User')} style={tab === 'User' ? ds.sideIconActive : ds.sideIcon}><Icons.User /><span style={ds.sideLabel}>USER</span></div>
        <div onClick={() => setTab('Catalog')} style={tab === 'Catalog' ? ds.sideIconActive : ds.sideIcon} title="Catálogo de Serviços"><Icons.Catalog /><span style={ds.sideLabel}>CATÁLOGO</span></div>
        <div onClick={handleLogout} style={ds.sideIcon}><Icons.Settings /><span style={ds.sideLabel}>SAIR</span></div>
      </aside>

      <main style={ds.main}>
        <header style={ds.header}>
          <div><h1 style={ds.welcomeText}>Bom dia, {adminInfo.name}</h1><p style={ds.subWelcome}>{loading ? 'Sincronizando...' : 'Sistema Online'}</p></div>
          <div style={ds.adminProfile}><div style={{textAlign: 'right'}}><p style={ds.adminName}>{adminInfo.name}</p><p style={ds.adminEmail}>{adminInfo.email}</p></div><div style={ds.avatar}>RR</div></div>
        </header>

        {tab === 'Home' ? (
          <div style={ds.grid}>
            <section style={ds.cardMain}>
              <div style={{display: 'flex', justifyContent: 'space-between'}}>
                <div>
                  <h3 style={{margin: 0, opacity: 0.8}}>Volume Financeiro (GTV)</h3>
                  <h2 style={{fontSize: '42px', margin: '10px 0'}}>R$ {stats.faturamento.toLocaleString('pt-BR')}</h2>
                </div>
                <div style={{textAlign: 'right'}}>
                  <span style={ds.trendTag}>📈 +12%</span>
                </div>
              </div>
              <div style={ds.miniStatsGrid}>
                <div style={ds.miniStat}><span>Receita Central</span><strong>R$ {stats.comissao.toLocaleString('pt-BR')}</strong></div>
                <div style={ds.miniStat}><span>Ticket Médio</span><strong>R$ 185,00</strong></div>
              </div>
            </section>
            <div style={{display: 'flex', flexDirection: 'column', gap: '20px'}}>
              <section style={ds.cardGreen}><h4>Novos Pedidos</h4><div style={{fontSize: '24px', fontWeight: 'bold'}}>{stats.novosPedidosCount}</div></section>
              <section style={ds.cardYellow}><h4>Serviços Pendentes</h4><div style={{fontSize: '24px', fontWeight: 'bold'}}>{stats.servicosPendentesCount}</div></section>
            </div>
            <section style={{...ds.cardWhite, gridColumn: '1 / 3'}}>
              <h4 style={{color: '#1e293b', marginBottom: '20px'}}>Últimos Pedidos</h4>
              {stats.pedidosRecentes.map(p => (
                <div key={p.id} style={ds.row}>
                  <div style={ds.rowIcon}>🚖</div>
                  <div style={{flex: 1}}>
                    <strong style={{color: '#1e293b'}}>{p.origem} → {p.destino}</strong>
                    <br/><small style={{color: '#64748b'}}>{p.status}</small>
                    {p.observacoes && <div style={{fontSize: '11px', color: THEME.secondary, marginTop: '5px', fontStyle: 'italic'}}>💬 "{p.observacoes}"</div>}
                  </div>
                  <div style={{fontWeight: 'bold', color: '#4c1d95'}}>R$ {parseFloat(p.valor || 0).toFixed(2)}</div>
                </div>
              ))}
            </section>
          </div>
        ) : tab === 'User' ? (
          <div style={{display: 'flex', flexDirection: 'column', gap: '25px'}}>
            {/* Seção de Aprovações Pendentes (Estilo Uber/99 Review) */}
            {motoristas.filter(m => m.status === 'PENDENTE_APROVACAO').length > 0 && (
              <div style={{...ds.cardWhite, border: `2px solid ${THEME.warning}`, animation: 'fadeIn 0.5s ease-in'}}>
                <h2 style={{color: THEME.warning, marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px'}}>
                  <span>⚠️</span> Novas Solicitações de Cadastro
                </h2>
                {motoristas.filter(m => m.status === 'PENDENTE_APROVACAO').map(m => (
                  <div key={m.id} style={ds.row}>
                    <div style={{flex: 1}}>
                      <strong style={{color: '#1e293b', fontSize: '16px'}}>{m.nome}</strong>
                      <br/><small style={{color: '#64748b'}}>{m.carro} • {m.placa} • {m.modelo}</small>
                    </div>
                    <div style={{display: 'flex', gap: '10px'}}>
                      <button style={{...ds.btnPrimary, background: THEME.success}} onClick={() => handleStatusMotorista(m.id, 'ATIVO')}>Aprovar ✅</button>
                      <button style={{...ds.btnOutline, color: THEME.danger, borderColor: THEME.danger}} onClick={() => handleStatusMotorista(m.id, 'REJEITADO')}>Rejeitar ❌</button>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Seção de Parceiros / Indicações */}
            <div style={ds.cardWhite}>
              <h2 style={{color: '#1e293b', marginBottom: '20px'}}>🤝 Rede de Parceiros (Indicações)</h2>
              <div style={ds.miniStatsGrid}>
                <div style={ds.statBox}>
                  <small style={ds.label}>Total a Pagar (Comissões)</small>
                  <strong style={{fontSize: '20px', color: THEME.danger}}>R$ 1.250,00</strong>
                </div>
                <div style={ds.statBox}>
                  <small style={ds.label}>Top Parceiro</small>
                  <strong style={{fontSize: '20px', color: THEME.primary}}>Hotel Master</strong>
                </div>
              </div>
              <div style={{marginTop: '20px'}}>
                <div style={ds.row}>
                  <div style={{flex: 1}}><strong>Concierge João</strong> <small>(Cod: JOAO10)</small></div>
                  <div style={{color: THEME.success}}>12 Reservas</div>
                  <div style={{display: 'flex', gap: '10px', alignItems: 'center'}}>
                    <div style={{fontWeight: 'bold'}}>R$ 340,00</div>
                    <button style={ds.btnOutline} onClick={() => abrirGeradorQR('JOAO10', 'Concierge João')}>QR Code 📱</button>
                  </div>
                </div>
              </div>
            </div>

            <div style={ds.cardWhite}>
              <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px'}}>
                <h2 style={{color: '#1e293b'}}>Frota de Motoristas</h2>
                <div style={{display: 'flex', gap: '10px', alignItems: 'center'}}>
                  <select 
                  style={{...ds.input, width: '180px', marginBottom: 0, padding: '10px'}} 
                  value={driverFilter} 
                  onChange={(e) => setDriverFilter(e.target.value)}
                >
                  <option value="ALL">Todas Categorias</option>
                  <option value="STANDARD">Standard</option>
                  <option value="PREMIUM">Premium</option>
                </select>
                <select 
                  style={{...ds.input, width: '180px', marginBottom: 0, padding: '10px'}} 
                  value={driverStatusFilter} 
                  onChange={(e) => setDriverStatusFilter(e.target.value)}
                >
                  <option value="ALL">Todos Status</option>
                  <option value="ALL">Todas Categorias</option>
                  <option value="STANDARD">Standard</option>
                  <option value="PREMIUM">Premium</option>
                </select>
                  <button style={ds.btnPrimary} onClick={() => setShowAddDriver(true)}>+ Novo Motorista</button>
                </div>
              </div>
              {motoristas
                .filter(m => (driverFilter === 'ALL' || m.categoria === driverFilter) && (driverStatusFilter === 'ALL' || m.status === driverStatusFilter))
                .map(m => (
                  <div key={m.id} style={ds.row}>
                    <div style={{flex: 1}}>
                      <div style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
                        <strong style={{color: '#1e293b'}}>{m.nome}</strong>
                        <span style={{...ds.badge, backgroundColor: m.categoria === 'PREMIUM' ? '#fef3c7' : '#f1f5f9', color: m.categoria === 'PREMIUM' ? '#92400e' : '#64748b'}}>
                          {m.categoria || 'STANDARD'}
                        </span>
                      </div>
                      <small style={{color: '#64748b'}}>{m.carro} • {m.placa} • {m.plano}</small>
                    </div>
                    <div style={{display: 'flex', gap: '10px'}}>
                      <button style={ds.btnOutline} onClick={() => abrirGeradorQR(m.telefone, m.nome)}>QR Link 🔗</button>
                      <button style={ds.btnOutline} onClick={() => alterarPlanoMotorista(m.id, m.plano)}>Plano</button>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        ) : tab === 'Stats' ? (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '25px' }}>
            <div style={ds.cardWhite}>
              <h3 style={{color: '#1e293b', marginBottom: '20px'}}>Evolução de Faturamento</h3>
              <div style={{height: '300px'}}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={stats.faturamentoHistorico}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0"/>
                    <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#64748b'}}/>
                    <YAxis hide/>
                    <Tooltip contentStyle={{borderRadius: '15px', border: 'none', boxShadow: '0 10px 25px rgba(0,0,0,0.1)'}}/>
                    <Line type="monotone" dataKey="valor" stroke="#4c1d95" strokeWidth={4} dot={{r: 6, fill: '#4c1d95', strokeWidth: 2, stroke: '#fff'}} activeDot={{r: 8}}/>
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div style={ds.cardWhite}>
              <h3 style={{color: '#1e293b', marginBottom: '20px'}}>Distribuição de Status</h3>
              <div style={{height: '300px'}}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={stats.statusChartData}
                      cx="50%" cy="50%"
                      innerRadius={60} outerRadius={80}
                      paddingAngle={5} dataKey="value"
                    >
                      {stats.statusChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={{borderRadius: '15px', border: 'none', boxShadow: '0 10px 25px rgba(0,0,0,0.1)'}} />
                    <Legend verticalAlign="bottom" height={36}/>
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        ) : tab === 'Catalog' ? (
          <div style={ds.cardWhite}>
            <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '20px'}}>
              <h2 style={{color: '#1e293b'}}>Gestão de Serviços e Experiências</h2>
              <button style={ds.btnPrimary} onClick={() => setShowAddService(true)}>+ Novo Item</button>
            </div>
            <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '20px'}}>
              {servicos.map(s => (
                <div key={s.id} style={ds.statBox}>
                  {s.imagem_url ? (
                    <img src={s.imagem_url} alt={s.nome} style={{width: '100%', height: '100px', objectFit: 'cover', borderRadius: '10px'}} />
                  ) : (
                    <div style={{height: '100px', background: '#e2e8f0', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>📸</div>
                  )}
                  <h4 style={{margin: '10px 0', fontSize: '14px'}}>{s.nome}</h4>
                  <div style={{fontWeight: 'bold', color: '#4c1d95'}}>R$ {parseFloat(s.valor || 0).toFixed(2)}</div>
                </div>
              ))}
            </div>
          </div>
        ) : tab === 'Live' ? (
          <div style={ds.cardWhite}>
            <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px'}}>
              <h2 style={{color: '#1e293b'}}>Monitoramento em Tempo Real</h2>
              <span style={{color: THEME.success, fontWeight: 'bold', fontSize: '12px'}}>● {motoristas.length} MOTORISTAS ATIVOS</span>
            </div>
            <div style={ds.mapLivePlaceholder}>
               <div style={ds.mapMarkerPulse} />
               <div style={{...ds.mapMarkerPulse, top: '40%', left: '30%', animationDelay: '0.5s'}} />
               <div style={{...ds.mapMarkerPulse, top: '60%', left: '70%', animationDelay: '1s'}} />
               <p style={{color: '#94a3b8', fontSize: '14px', zIndex: 1}}>Integrando camada de geolocalização por satélite...</p>
               <div style={ds.mapGridOverlay} />
            </div>
          </div>
        ) : (
          <div style={ds.cardWhite}>Selecione uma opção no menu lateral.</div>
        )}

        {showAddDriver && (
          <div style={ds.formOverlay}>
            <form style={ds.formCard} onSubmit={cadastrarMotorista}>
              <h2 style={{color: '#4c1d95', marginBottom: '25px', textAlign: 'center'}}>Novo Parceiro de Frota</h2>
              
              <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px'}}>
                <div>
                  <label style={ds.label}>Nome Completo</label>
                  <input style={ds.input} placeholder="Ex: João Silva" value={newDriver.nome} onChange={e => setNewDriver({...newDriver, nome: e.target.value})} required/>
                </div>
                <div>
                  <label style={ds.label}>WhatsApp</label>
                  <input style={ds.input} placeholder="5554..." value={newDriver.telefone} onChange={e => setNewDriver({...newDriver, telefone: e.target.value})} required/>
                </div>
                <div>
                  <label style={ds.label}>Carro</label>
                  <input style={ds.input} placeholder="Ex: Spin" value={newDriver.carro} onChange={e => setNewDriver({...newDriver, carro: e.target.value})} required/>
                </div>
                <div>
                  <label style={ds.label}>Placa</label>
                  <input style={ds.input} placeholder="ABC-1234" value={newDriver.placa} onChange={e => setNewDriver({...newDriver, placa: e.target.value})} required/>
                </div>
                <div>
                  <label style={ds.label}>Modelo (Versão)</label>
                  <input style={ds.input} placeholder="Ex: LTZ" value={newDriver.modelo} onChange={e => setNewDriver({...newDriver, modelo: e.target.value})} required/>
                </div>
                <div>
                  <label style={ds.label}>Ano do Veículo</label>
                  <input type="number" style={ds.input} placeholder="2024" value={newDriver.ano} onChange={e => setNewDriver({...newDriver, ano: parseInt(e.target.value)})} required/>
                </div>
                <div>
                  <label style={ds.label}>Plano Inicial</label>
                  <select style={ds.input} value={newDriver.plano} onChange={e => setNewDriver({...newDriver, plano: e.target.value})}>
                    <option value="MENSAL">Mensalidade Fixa</option>
                    <option value="MASTER">Comissão Master (20%)</option>
                  </select>
                </div>
                <div>
                  <label style={ds.label}>Categoria do Veículo</label>
                  <select style={ds.input} value={newDriver.categoria} onChange={e => setNewDriver({...newDriver, categoria: e.target.value})}>
                    <option value="STANDARD">Standard</option>
                    <option value="PREMIUM">Premium</option>
                  </select>
                </div>
              </div>

              <div style={{display: 'flex', gap: '10px', marginTop: '20px'}}>
                <button type="submit" style={ds.btnPrimary}>Confirmar</button>
                <button type="button" style={ds.btnOutline} onClick={() => setShowAddDriver(false)}>Cancelar</button>
              </div>
            </form>
          </div>
        )}

        {showAddService && (
          <div style={ds.formOverlay}>
            <form style={ds.formCard} onSubmit={cadastrarServico}>
              <h2 style={{color: '#4c1d95', marginBottom: '25px', textAlign: 'center'}}>Novo Item no Catálogo</h2>
              <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px'}}>
                <div style={{gridColumn: '1 / 3'}}>
                  <label style={ds.label}>Nome do Serviço/Experiência</label>
                  <input style={ds.input} placeholder="Ex: Tour Uva e Vinho" value={newService.nome} onChange={e => setNewService({...newService, nome: e.target.value})} required/>
                </div>
                <div>
                  <label style={ds.label}>Categoria</label>
                  <select style={ds.input} value={newService.categoria} onChange={e => setNewService({...newService, categoria: e.target.value})}>
                    <option value="TRANSFERS">Transfers</option>
                    <option value="INGRESSOS">Ingressos</option>
                    <option value="PACOTES">Pacotes</option>
                    <option value="EXPERIENCIAS">Experiências</option>
                  </select>
                </div>
                <div>
                  <label style={ds.label}>Preço Base (R$)</label>
                  <input type="number" style={ds.input} placeholder="150.00" value={newService.valor} onChange={e => setNewService({...newService, valor: e.target.value})} required/>
                </div>
                <div style={{gridColumn: '1 / 3'}}>
                  <label style={ds.label}>Descrição Curta</label>
                  <textarea style={{...ds.input, height: '80px', resize: 'none'}} placeholder="Detalhes que o cliente verá no site..." value={newService.descricao} onChange={e => setNewService({...newService, descricao: e.target.value})} required/>
                </div>
                <div style={{gridColumn: '1 / 3'}}>
                  <label style={ds.label}>Foto de Capa</label>
                  <input type="file" accept="image/*" onChange={e => setNewService({...newService, imagem: e.target.files[0]})} />
                </div>
              </div>
              <div style={{display: 'flex', gap: '10px', marginTop: '20px'}}>
                <button type="submit" style={ds.btnPrimary}>Salvar no Catálogo</button>
                <button type="button" style={ds.btnOutline} onClick={() => setShowAddService(false)}>Cancelar</button>
              </div>
            </form>
          </div>
        )}

        {showSuccessAnimation && (
          <div style={ds.successOverlay}>
            <style>{`
              @keyframes popIn { from { transform: scale(0.5); opacity: 0; } to { transform: scale(1); opacity: 1; } }
              @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
            `}</style>
            <div style={ds.successCheck}>
              ✅
            </div>
          </div>
        )}

        {qrModal.open && (
          <div style={ds.formOverlay} onClick={() => setQrModal({ ...qrModal, open: false })}>
            <div style={{...ds.formCard, maxWidth: '400px', textAlign: 'center'}} onClick={e => e.stopPropagation()}>
              <h2 style={{color: THEME.primary, marginBottom: '10px'}}>{qrModal.title}</h2>
              <p style={{fontSize: '14px', color: THEME.textLight, marginBottom: '20px'}}>Link de Indicação Exclusivo</p>
              
              <div style={{background: '#fff', padding: '20px', borderRadius: '20px', display: 'inline-block', boxShadow: '0 4px 15px rgba(0,0,0,0.1)'}}>
                <img 
                  src={`https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(qrModal.link)}`} 
                  alt="QR Code de Indicação"
                />
              </div>
              
              <p style={{marginTop: '20px', fontSize: '11px', wordBreak: 'break-all', color: THEME.secondary}}>{qrModal.link}</p>
              <button style={{...ds.btnPrimary, marginTop: '20px', width: '100%'}} onClick={() => setQrModal({ ...qrModal, open: false })}>Fechar</button>
            </div>
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
        <Route path="/driver" element={<ProtectedRoute allowedRoles={['motorista', 'admin']}><DriverApp /></ProtectedRoute>} />
        <Route path="/store" element={<Storefront />} />
        <Route path="/success" element={<Success />} />
        <Route path="/failure" element={<Failure />} />
        <Route 
          path="/dashboard" 
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <Dashboard />
            </ProtectedRoute>
          } 
        />
        <Route path="/" element={<Navigate to="/dashboard" />} />
      </Routes>
    </Router>
  );
}

const ds = {
  wrapper: { display: 'flex', height: '100vh', width: '100vw', background: '#f8fafc', overflow: 'hidden', fontFamily: '"Inter", sans-serif' },
  sidebar: { width: '100px', background: '#fff', borderRight: '1px solid #e2e8f0', display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '40px 0' },
  sideIcon: { cursor: 'pointer', marginBottom: '30px', color: '#94a3b8', display: 'flex', flexDirection: 'column', alignItems: 'center', transition: 'all 0.2s', width: '100%' },
  sideIconActive: { cursor: 'pointer', marginBottom: '30px', color: '#4c1d95', display: 'flex', flexDirection: 'column', alignItems: 'center', transition: 'all 0.2s', width: '100%', borderLeft: '4px solid #4c1d95' },
  sideLabel: { fontSize: '10px', fontWeight: 'bold', marginTop: '5px' },
  main: { flex: 1, padding: '40px', overflowY: 'auto', background: '#f8fafc' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '40px', paddingRight: '20px' },
  mapLivePlaceholder: { height: '500px', background: '#e2e8f0', borderRadius: '30px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', position: 'relative', overflow: 'hidden', border: '2px solid #fff' },
  mapGridOverlay: { position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', backgroundImage: 'linear-gradient(#cbd5e1 1px, transparent 1px), linear-gradient(90deg, #cbd5e1 1px, transparent 1px)', backgroundSize: '40px 40px', opacity: 0.2 },
  mapMarkerPulse: { 
    position: 'absolute', width: '12px', height: '12px', background: '#4c1d95', borderRadius: '50%', 
    boxShadow: '0 0 0 10px rgba(76, 29, 149, 0.2)', animation: 'popIn 1.5s infinite alternate' 
  },
  welcomeText: { fontSize: '28px', margin: 0, color: '#1e293b', fontWeight: '800' },
  subWelcome: { color: '#475569', margin: '5px 0 0 0', fontWeight: '500' },
  adminProfile: { display: 'flex', alignItems: 'center', gap: '15px' },
  adminName: { margin: 0, fontWeight: '700', color: '#1e293b' },
  adminEmail: { margin: 0, fontSize: '12px', color: '#64748b', fontWeight: '400' },
  avatar: { width: '45px', height: '45px', background: '#4c1d95', color: '#fff', borderRadius: '15px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' },
  grid: { display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '25px' },
  cardMain: { background: 'linear-gradient(135deg, #4c1d95 0%, #6d28d9 100%)', borderRadius: '30px', padding: '30px', color: '#fff', boxShadow: '0 15px 35px rgba(76, 29, 149, 0.25)', border: '1px solid rgba(255,255,255,0.1)' },
  cardGreen: { background: 'linear-gradient(135deg, #059669 0%, #10b981 100%)', borderRadius: '30px', padding: '30px', color: '#fff', boxShadow: '0 15px 35px rgba(5, 150, 105, 0.2)' },
  cardYellow: { background: 'linear-gradient(135deg, #d97706 0%, #f59e0b 100%)', borderRadius: '30px', padding: '30px', color: '#fff', boxShadow: '0 15px 35px rgba(217, 119, 6, 0.2)' },
  cardWhite: { background: '#fff', borderRadius: '30px', padding: '30px', border: '1px solid #e2e8f0', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' },
  row: { display: 'flex', alignItems: 'center', gap: '15px', padding: '15px 0', borderBottom: '1px solid #f1f5f9' },
  rowIcon: { width: '40px', height: '40px', background: '#f1f5f9', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '18px' },
  trendTag: { background: 'rgba(255,255,255,0.2)', padding: '5px 12px', borderRadius: '20px', fontSize: '12px', fontWeight: 'bold' },
  miniStatsGrid: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginTop: '20px', borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '20px' },
  miniStat: { display: 'flex', flexDirection: 'column', gap: '5px', fontSize: '13px' },
  badge: { fontSize: '10px', padding: '2px 8px', borderRadius: '10px', fontWeight: 'bold' },
  status_PAGO: { background: '#dcfce7', color: '#166534' },
  status_ACEITO: { background: '#dbeafe', color: '#1e40af' },
  status_PENDENTE: { background: '#fef3c7', color: '#92400e' },
  formOverlay: { position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000, backdropFilter: 'blur(5px)' },
  formCard: { background: '#fff', padding: '40px', borderRadius: '30px', width: '95%', maxWidth: '700px', boxShadow: '0 25px 50px rgba(0,0,0,0.1)' },
  input: { width: '100%', padding: '14px', borderRadius: '12px', border: '1px solid #cbd5e1', marginBottom: '10px', color: '#1e293b', background: '#fff', fontWeight: '500', outline: 'none' },
  label: { display: 'block', marginBottom: '5px', fontSize: '12px', fontWeight: 'bold', color: '#475569', marginLeft: '5px' },
  btnPrimary: { background: '#4c1d95', color: '#fff', border: 'none', padding: '12px 25px', borderRadius: '12px', fontWeight: 'bold', cursor: 'pointer' },
  btnOutline: { background: 'transparent', border: '1px solid #cbd5e1', padding: '8px 15px', borderRadius: '10px', fontSize: '12px', color: '#1e293b', cursor: 'pointer', fontWeight: '600' },
  statBox: { flex: 1, padding: '20px', background: '#f8fafc', borderRadius: '20px', border: '1px solid #e2e8f0' },
  successOverlay: {
    position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
    background: 'rgba(0,0,0,0.6)', display: 'flex', justifyContent: 'center', alignItems: 'center',
    zIndex: 2000, backdropFilter: 'blur(8px)', animation: 'fadeIn 0.3s ease-out'
  },
  successCheck: {
    fontSize: '80px', color: '#10b981', background: '#fff', borderRadius: '50%',
    width: '120px', height: '120px', display: 'flex', justifyContent: 'center', alignItems: 'center',
    boxShadow: '0 10px 30px rgba(0,0,0,0.3)', animation: 'popIn 0.4s cubic-bezier(0.68, -0.55, 0.27, 1.55)'
  }
};