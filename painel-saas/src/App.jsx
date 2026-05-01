import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate, Navigate } from 'react-router-dom';
import axios from 'axios';
import Login from './Login';

// Configuração da API baseada no ambiente
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8001';

// Componentes de Ícones (SVG) para evitar dependências extras e manter o estilo leve
const Icons = {
  Home: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>,
  Stats: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>,
  User: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>,
  Settings: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>,
  Plans: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>,
};

function Dashboard() {
  const navigate = useNavigate();
  
  // ESTADOS PARA CONTROLE DE TELA E DADOS REAIS
  const [tab, setTab] = useState('Home');
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({ faturamento: 0, pedidosRecentes: [], totalMotoristas: 0 });
  const [motoristas, setMotoristas] = useState([]);
  const [adminInfo, setAdminInfo] = useState({ name: "Renato Rocha", email: "renato@centraltransfers.com" });

  // BUSCA DE DADOS REAIS DO BACKEND FASTAPI
  const carregarDadosReais = async () => {
    setLoading(true);
    try {
      const [pedidosRes, motoristasRes] = await Promise.all([
        axios.get(`${API_URL}/pedidos`),
        axios.get(`${API_URL}/motoristas`)
      ]);

      const faturamentoTotal = pedidosRes.data
        .filter(p => ['PAGO', 'CONCLUIDO', 'ACEITO'].includes(p.status))
        .reduce((acc, p) => acc + (p.valor || 0), 0);

      setMotoristas(motoristasRes.data);
      setStats({
        faturamento: faturamentoTotal,
        pedidosRecentes: pedidosRes.data.slice(-5).reverse(), // Últimos 5 pedidos
        totalMotoristas: motoristasRes.data.length
      });
    } catch (error) {
      console.error("Erro ao carregar dados do SaaS:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    carregarDadosReais();
  }, []);

  return (
    <div style={ds.wrapper}>
      <aside style={ds.sidebar}>
        <div style={{fontSize: '24px', marginBottom: '30px'}}>🚐</div>
        
        {/* BOTÕES COM LÓGICA DE TROCA DE ABA */}
        <div onClick={() => setTab('Home')} style={tab === 'Home' ? ds.sideIconActive : ds.sideIcon} title="Painel Principal">
          <Icons.Home /><span style={ds.sideLabel}>HOME</span>
        </div>
        <div onClick={() => setTab('Stats')} style={tab === 'Stats' ? ds.sideIconActive : ds.sideIcon} title="Relatórios Financeiros">
          <Icons.Stats /><span style={ds.sideLabel}>STAT</span>
        </div>
        <div onClick={() => setTab('User')} style={tab === 'User' ? ds.sideIconActive : ds.sideIcon} title="Frota e Planos">
          <Icons.User /><span style={ds.sideLabel}>USER</span>
        </div>
        <div onClick={() => setTab('Plans')} style={tab === 'Plans' ? ds.sideIconActive : ds.sideIcon} title="Configuração de Planos">
          <Icons.Plans /><span style={ds.sideLabel}>PLANS</span>
        </div>
        
        <div onClick={() => { if(window.confirm("Sair do sistema?")) navigate('/login') }} style={ds.sideIcon}>
          <Icons.Settings /><span style={ds.sideLabel}>SAIR</span>
        </div>
      </aside>

      <main style={ds.main}>
        <header style={ds.header}>
          <div>
            <h1 style={ds.welcomeText}>Bom dia, <span style={{fontWeight:800}}>{adminInfo.name}</span></h1>
            <p style={ds.subWelcome}>Status: {loading ? 'Atualizando...' : 'Sistema Online'}</p>
          </div>
          <div style={ds.adminProfile}>
            <div style={ds.adminTextGroup}>
              <p style={ds.adminName}>{adminInfo.name}</p>
              <p style={ds.adminEmail}>{adminInfo.email}</p>
            </div>
            <div style={ds.avatar}>RR</div>
          </div>
        </header>

        {/* CONTEÚDO DINÂMICO BASEADO NA ABA SELECIONADA */}
        {tab === 'Home' ? (
          <div style={ds.grid}>
            <section style={ds.cardMain} onClick={carregarDadosReais}>
              <div style={{display:'flex', justifyContent:'space-between'}}>
                <h3 style={{margin:0}}>Faturamento Total (SaaS)</h3>
                <small>{loading ? '...' : '🔄 Sincronizado'}</small>
              </div>
              <h2 style={{fontSize: '34px', margin: '20px 0'}}>
                R$ {stats.faturamento.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
              </h2>
              <div style={ds.chartContainer}>
                {[20, 45, 30, 85, 40, 60, 90].map((h, i) => (
                  <div key={i} style={{...ds.bar, height: `${h}%`, background: h === 85 ? '#fff' : 'rgba(255,255,255,0.3)'}}></div>
                ))}
              </div>
            </section>

            <section style={ds.cardBlack}>
              <p style={{fontSize: '11px', opacity: 0.6}}>Ação Rápida</p>
              <h4 style={{margin: '5px 0 20px 0'}}>Monitoramento</h4>
              <div style={{fontSize: '24px', fontWeight: 'bold'}}>{stats.totalMotoristas || 0}</div>
              <p style={{fontSize: '12px'}}>Motoristas Ativos</p>
              <button style={{...ds.btnSmall, marginTop: '15px'}} onClick={() => setTab('User')}>Gerenciar Frota</button>
            </section>

            <section style={ds.cardWhite}>
              <h4>Últimos Pedidos (Real-time)</h4>
              {stats.pedidosRecentes.map((pedido) => (
                <div key={pedido.id} style={ds.row} onClick={() => alert(`Pedido de ${pedido.origem} para ${pedido.destino}`)}>
                  <div style={ds.rowIcon}>{pedido.status === 'PAGO' ? '✅' : '⏳'}</div>
                  <div style={{flex: 1}}>
                    <div style={{fontSize: '14px', fontWeight: 'bold'}}>{pedido.origem} → {pedido.destino}</div>
                    <small style={{opacity: 0.6}}>{pedido.status}</small>
                  </div>
                  <div style={{fontWeight:'bold', color:'#4c1d95'}}>R$ {pedido.valor}</div>
                </div>
              ))}
              {stats.pedidosRecentes.length === 0 && <p style={{textAlign:'center', fontSize: '13px', opacity: 0.5}}>Nenhuma atividade hoje.</p>}
            </section>
          </div>
        ) : tab === 'User' ? (
          <div style={ds.cardWhite}>
            <h3>Gestão de Motoristas & Planos</h3>
            {motoristas.map(m => (
              <div key={m.id} style={ds.row}>
                <div style={ds.avatarSmall}>{m.nome[0]}</div>
                <div style={{flex: 1}}>
                  <strong>{m.nome}</strong>
                  <div style={{fontSize: '12px', color: '#64748b'}}>{m.carro} - {m.placa}</div>
                </div>
                <div style={m.plano === 'MASTER' ? ds.badgeGold : ds.badgeBlue}>
                  {m.plano || 'MENSAL'}
                </div>
                <button style={ds.btnOutline}>Alterar Plano</button>
              </div>
            ))}
          </div>
        ) : tab === 'Plans' ? (
          <div style={ds.grid}>
            <div style={ds.cardPlan}>
              <h2 style={{color: '#4c1d95'}}>Plano Profissional</h2>
              <p>R$ 199,00 / mês</p>
              <ul style={ds.planList}>
                <li>Até 50 corridas/mês</li>
                <li>Suporte prioridário</li>
                <li>Zero comissão</li>
              </ul>
              <button style={ds.btnPrimary}>Editar Oferta</button>
            </div>
            <div style={{...ds.cardPlan, border: '2px solid #4c1d95'}}>
              <h2 style={{color: '#4c1d95'}}>Plano Master 🏆</h2>
              <p>R$ 0,00 mensalidade</p>
              <ul style={ds.planList}>
                <li>Corridas Ilimitadas</li>
                <li>Taxa fixa: 20% por serviço</li>
                <li>Pagamento sob demanda</li>
              </ul>
              <button style={ds.btnPrimary}>Editar Oferta</button>
            </div>
          </div>
        ) : (
          <div style={{padding: '50px', textAlign: 'center', background: '#fff', borderRadius: '30px'}}>
            <h2>Tela de {tab} em desenvolvimento...</h2>
            <p>Em breve você verá os gráficos detalhados aqui.</p>
          </div>
        )}
      </main>
    </div>
  );
}

// --- DESIGN SYSTEM (ESTILOS MODERNOS E VENDÁVEIS) ---
const ds = {
  wrapper: {
    display: 'flex', height: '100vh', width: '100vw', background: '#f8fafc', overflow: 'hidden', fontFamily: '"Inter", sans-serif'
  },
  sidebar: {
    width: '100px', background: '#fff', borderRight: '1px solid #e2e8f0', display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '40px 0'
  },
  sideIcon: {
    cursor: 'pointer', marginBottom: '30px', color: '#94a3b8', display: 'flex', flexDirection: 'column', alignItems: 'center', transition: 'all 0.2s', width: '100%'
  },
  sideIconActive: {
    cursor: 'pointer', marginBottom: '30px', color: '#4c1d95', display: 'flex', flexDirection: 'column', alignItems: 'center', transition: 'all 0.2s', width: '100%', borderLeft: '4px solid #4c1d95'
  },
  sideLabel: { fontSize: '10px', fontWeight: 'bold', marginTop: '5px' },
  main: { flex: 1, padding: '40px', overflowY: 'auto' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '40px' },
  welcomeText: { fontSize: '24px', margin: 0, color: '#1e293b' },
  subWelcome: { color: '#64748b', margin: '5px 0 0 0' },
  adminProfile: { display: 'flex', alignItems: 'center', gap: '15px' },
  adminTextGroup: { textAlign: 'right' },
  adminName: { margin: 0, fontWeight: 'bold', color: '#1e293b' },
  adminEmail: { margin: 0, fontSize: '12px', color: '#64748b' },
  avatar: { width: '45px', height: '45px', background: '#4c1d95', color: '#fff', borderRadius: '15px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' },
  grid: { display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '25px' },
  cardMain: {
    background: 'linear-gradient(135deg, #4c1d95 0%, #7c3aed 100%)', borderRadius: '30px', padding: '30px', color: '#fff', cursor: 'pointer', boxShadow: '0 20px 40px rgba(76, 29, 149, 0.2)', transition: 'transform 0.2s'
  },
  chartContainer: { display: 'flex', alignItems: 'flex-end', gap: '8px', height: '60px', marginTop: '20px' },
  bar: { width: '100%', borderRadius: '4px' },
  cardBlack: {
    background: '#1e293b', borderRadius: '30px', padding: '30px', color: '#fff'
  },
  cardWhite: {
    gridColumn: '1 / 3', background: '#fff', borderRadius: '30px', padding: '30px', border: '1px solid #e2e8f0', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
  },
  btnSmall: {
    background: 'rgba(255,255,255,0.1)', border: 'none', color: '#fff', padding: '10px 20px', borderRadius: '12px', cursor: 'pointer', fontSize: '12px', fontWeight: 'bold', transition: 'background 0.2s'
  },
  row: {
    display: 'flex', alignItems: 'center', gap: '15px', padding: '15px 0', borderBottom: '1px solid #f1f5f9', cursor: 'pointer', transition: 'background 0.2s'
  },
  rowIcon: { width: '40px', height: '40px', background: '#f1f5f9', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '18px' },
  avatarSmall: { width: '35px', height: '35px', background: '#e2e8f0', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', color: '#4c1d95' },
  badgeGold: { background: '#fef3c7', color: '#92400e', padding: '4px 12px', borderRadius: '20px', fontSize: '11px', fontWeight: 'bold' },
  badgeBlue: { background: '#dbeafe', color: '#1e40af', padding: '4px 12px', borderRadius: '20px', fontSize: '11px', fontWeight: 'bold' },
  btnOutline: { background: 'transparent', border: '1px solid #e2e8f0', padding: '8px 15px', borderRadius: '10px', fontSize: '12px', cursor: 'pointer' },
  cardPlan: { background: '#fff', padding: '40px', borderRadius: '30px', textAlign: 'center', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)' },
  planList: { listStyle: 'none', padding: 0, margin: '30px 0', textAlign: 'left', fontSize: '14px', color: '#64748b' },
  btnPrimary: { background: '#4c1d95', color: '#fff', border: 'none', padding: '12px 25px', borderRadius: '12px', fontWeight: 'bold', cursor: 'pointer', width: '100%' }
};

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