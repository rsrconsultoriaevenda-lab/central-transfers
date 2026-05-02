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

const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('token');
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

const Icons = {
  Home: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>,
  Stats: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M6 20V10M12 20V4M18 20V14"/></svg>,
  User: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="7" r="4"/><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/></svg>,
  Catalog: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82zM6.5 8.5a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3z"/></svg>,
  Settings: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
};

function Dashboard() {
  const navigate = useNavigate();

  const [tab, setTab] = useState('Home');
  const [loading, setLoading] = useState(false);
  const [showAddDriver, setShowAddDriver] = useState(false);
  const [showAddService, setShowAddService] = useState(false);
  const [showSuccessAnimation, setShowSuccessAnimation] = useState(false);

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

  const adminInfo = { name: "Renato Rocha", email: "renato@centraltransfers.com" };
  const COLORS = ['#4c1d95', '#10b981', '#f59e0b', '#3b82f6', '#ef4444'];

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

  const cadastrarMotorista = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await axios.post(`${API_URL}/motoristas`, newDriver, { headers: getAuthHeader() });
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
    formData.append('valor', newService.valor);
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
  }, []);

  return (
    <div style={ds.wrapper}>
      <aside style={ds.sidebar}>
        <div style={{fontSize: '24px', marginBottom: '30px'}}>🚐</div>
        <div onClick={() => setTab('Home')} style={tab === 'Home' ? ds.sideIconActive : ds.sideIcon}><Icons.Home /><span style={ds.sideLabel}>HOME</span></div>
        <div onClick={() => setTab('Stats')} style={tab === 'Stats' ? ds.sideIconActive : ds.sideIcon}><Icons.Stats /><span style={ds.sideLabel}>STAT</span></div>
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
              <h3 style={{margin: 0}}>Faturamento Total</h3>
              <h2 style={{fontSize: '34px', margin: '20px 0'}}>R$ {stats.faturamento.toLocaleString('pt-BR')}</h2>
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
                  </div>
                  <div style={{fontWeight: 'bold', color: '#4c1d95'}}>R$ {parseFloat(p.valor || 0).toFixed(2)}</div>
                </div>
              ))}
            </section>
          </div>
        ) : tab === 'User' ? (
          <div style={ds.cardWhite}>
            <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '20px'}}>
              <h2 style={{color: '#1e293b'}}>Frota de Motoristas</h2>
              <button style={ds.btnPrimary} onClick={() => setShowAddDriver(true)}>+ Novo Motorista</button>
            </div>
            {motoristas.map(m => (
              <div key={m.id} style={ds.row}>
                <div style={{flex: 1}}>
                  <strong style={{color: '#1e293b'}}>{m.nome}</strong>
                  <br/><small style={{color: '#64748b'}}>{m.carro} • {m.placa} • {m.plano}</small>
                </div>
                <button style={ds.btnOutline} onClick={() => alterarPlanoMotorista(m.id, m.plano)}>Trocar Plano</button>
              </div>
            ))}
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
      </main>
    </div>
  );
}

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route 
          path="/dashboard" 
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } 
        />
        <Route path="/" element={<Navigate to="/login" />} />
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