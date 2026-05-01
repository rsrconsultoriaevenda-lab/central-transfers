import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate, Navigate } from 'react-router-dom';

// --- BIBLIOTECA DE ÍCONES SVG (Design Realista) ---
const Icons = {
  Geral: () => (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 3v18h18"/><path d="M18 17V9"/><path d="M13 17V5"/><path d="M8 17v-3"/></svg>
  ),
  Frota: () => (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="1" y="3" width="22" height="13" rx="2" ry="2"/><path d="M7 21h0"/><path d="M17 21h0"/><path d="M4 16v2"/><path d="M20 16v2"/></svg>
  ),
  Precos: () => (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><path d="M16 8h-6a2 2 0 1 0 0 4h4a2 2 0 1 1 0 4H8"/><path d="M12 18V6"/></svg>
  ),
  Sair: () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
  )
};

// --- COMPONENTE: LOGIN ---
function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = (e) => {
    e.preventDefault();
    if (email && password) navigate('/dashboard');
  };

  return (
    <div style={loginStyles.pageWrapper}>
      <style>{`
        @keyframes gradientBG { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
        @keyframes vanTravel { from { left: -150px; } to { left: 100%; } }
      `}</style>
      <div style={loginStyles.cityOverlay}></div>
      <div style={loginStyles.glassCard}>
        <div style={loginStyles.iconCircle}>🚐</div>
        <h1 style={loginStyles.title}>Central Transfers</h1>
        <p style={loginStyles.subtitle}>Gestão de Frota Premium em Gramado</p>
        <form onSubmit={handleLogin}>
          <input 
            type="email" placeholder="E-mail" style={loginStyles.input} 
            value={email} onChange={(e) => setEmail(e.target.value)} required 
          />
          <input 
            type="password" placeholder="Senha" style={loginStyles.input} 
            value={password} onChange={(e) => setPassword(e.target.value)} required 
          />
          <button type="submit" style={loginStyles.button}>Entrar no Painel</button>
        </form>
      </div>
      <div style={loginStyles.roadLine}><div style={loginStyles.animatedVan}>🚐💨</div></div>
    </div>
  );
}

// --- COMPONENTE: DASHBOARD ---
function Dashboard() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('Geral');

  return (
    <div style={dashStyles.appContainer}>
      <aside style={dashStyles.sidebar}>
        <div style={dashStyles.logo}>🚐</div>
        <nav style={dashStyles.nav}>
          <button onClick={() => setActiveTab('Geral')} style={activeTab === 'Geral' ? dashStyles.activeBtn : dashStyles.navBtn}><Icons.Geral /></button>
          <button onClick={() => setActiveTab('Frota')} style={activeTab === 'Frota' ? dashStyles.activeBtn : dashStyles.navBtn}><Icons.Frota /></button>
          <button onClick={() => setActiveTab('Preços')} style={activeTab === 'Preços' ? dashStyles.activeBtn : dashStyles.navBtn}><Icons.Precos /></button>
        </nav>
        <button onClick={() => navigate('/login')} style={dashStyles.logoutBtn}><Icons.Sair /></button>
      </aside>

      <main style={dashStyles.main}>
        <header style={dashStyles.header}>
          <h2 style={{margin:0}}>Painel de Controle</h2>
          <div style={dashStyles.profile}>
            <div style={dashStyles.avatar}>AD</div>
            <span>Administrador</span>
          </div>
        </header>

        {activeTab === 'Geral' && (
          <div style={dashStyles.grid}>
            <div style={dashStyles.cardPurple}>
              <p>Faturamento Mensal</p>
              <h3>R$ 45.200,00</h3>
            </div>
            <div style={dashStyles.cardWhite}>
              <p>Serviços Hoje</p>
              <h3>18 Agendados</h3>
            </div>
          </div>
        )}
        
        {/* Aqui você pode adicionar as outras telas (Frota, Preços) conforme os códigos anteriores */}
      </main>
    </div>
  );
}

// --- ESTILOS ---
const loginStyles = {
  pageWrapper: { height: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center', background: 'linear-gradient(-45deg, #1e1b4b, #4c1d95, #7c3aed, #1e1b4b)', backgroundSize: '400% 400%', animation: 'gradientBG 12s ease infinite', position: 'relative', overflow: 'hidden', fontFamily: 'sans-serif' },
  cityOverlay: { position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, backgroundImage: 'url("https://images.unsplash.com/photo-1626014903708-3607062400f0?q=80&w=2000")', backgroundSize: 'cover', opacity: 0.1, mixBlendMode: 'overlay' },
  glassCard: { background: 'rgba(255, 255, 255, 0.1)', backdropFilter: 'blur(20px)', padding: '50px', borderRadius: '30px', width: '350px', textAlign: 'center', border: '1px solid rgba(255,255,255,0.2)', zIndex: 10 },
  iconCircle: { fontSize: '40px', marginBottom: '20px' },
  title: { color: '#fff', fontSize: '24px', margin: '0 0 10px 0' },
  subtitle: { color: 'rgba(255,255,255,0.6)', fontSize: '14px', marginBottom: '30px' },
  input: { width: '100%', padding: '15px', marginBottom: '15px', borderRadius: '12px', border: 'none', background: 'rgba(0,0,0,0.2)', color: '#fff', boxSizing: 'border-box' },
  button: { width: '100%', padding: '15px', borderRadius: '12px', border: 'none', background: '#fff', color: '#4c1d95', fontWeight: 'bold', cursor: 'pointer' },
  roadLine: { position: 'absolute', bottom: '50px', width: '100%', height: '1px', background: 'rgba(255,255,255,0.1)' },
  animatedVan: { position: 'absolute', bottom: '5px', fontSize: '30px', animation: 'vanTravel 15s linear infinite' }
};

const dashStyles = {
  appContainer: { display: 'flex', height: '100vh', backgroundColor: '#f8fafc', fontFamily: 'sans-serif' },
  sidebar: { width: '80px', backgroundColor: '#fff', borderRight: '1px solid #e2e8f0', display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '20px 0' },
  logo: { fontSize: '24px', marginBottom: '40px' },
  nav: { flex: 1, display: 'flex', flexDirection: 'column', gap: '20px' },
  navBtn: { background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', padding: '12px', borderRadius: '12px' },
  activeBtn: { background: '#f5f3ff', border: 'none', color: '#7c3aed', cursor: 'pointer', padding: '12px', borderRadius: '12px' },
  logoutBtn: { background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer' },
  main: { flex: 1, padding: '40px' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' },
  profile: { display: 'flex', alignItems: 'center', gap: '10px' },
  avatar: { width: '35px', height: '35px', background: '#7c3aed', color: '#fff', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', fontSize: '12px' },
  grid: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' },
  cardPurple: { background: 'linear-gradient(135deg, #7c3aed, #db2777)', padding: '30px', borderRadius: '20px', color: '#fff' },
  cardWhite: { background: '#fff', padding: '30px', borderRadius: '20px', border: '1px solid #e2e8f0' }
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