import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate, Navigate } from 'react-router-dom';

// --- ÍCONES ---
const Icons = {
  Home: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/></svg>,
  Stats: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M5 9.2h3V19H5zM10.6 5h2.8V19h-2.8zm5.6 8H19v6h-2.8z"/></svg>,
  User: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>,
  Settings: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.09.63-.09.94s.02.64.07.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/></svg>,
};

function Login() {
  const navigate = useNavigate();
  return (
    <div style={loginStyles.wrapper}>
      <div style={loginStyles.card}>
        <h2>Central Transfers</h2>
        <button style={loginStyles.btn} onClick={() => navigate('/dashboard')}>Acessar Painel</button>
      </div>
    </div>
  );
}

function Dashboard() {
  const navigate = useNavigate();
  const [tab, setTab] = useState('Home');
  const adminInfo = { name: "Alex Turner", email: "admin@centraltransfers.com", role: "Gestor de Frota" };

  return (
    <div style={ds.wrapper}>
      <aside style={ds.sidebar}>
        <div style={ds.logo}>🚐</div>
        <div onClick={() => setTab('Home')} style={tab === 'Home' ? ds.sideIconActive : ds.sideIcon}>
          <Icons.Home /><span style={ds.sideLabel}>HOME</span>
        </div>
        <div onClick={() => setTab('Stats')} style={tab === 'Stats' ? ds.sideIconActive : ds.sideIcon}>
          <Icons.Stats /><span style={ds.sideLabel}>STAT</span>
        </div>
        <div onClick={() => setTab('User')} style={tab === 'User' ? ds.sideIconActive : ds.sideIcon}>
          <Icons.User /><span style={ds.sideLabel}>USER</span>
        </div>
        <div onClick={() => navigate('/login')} style={ds.sideIcon}>
          <Icons.Settings /><span style={ds.sideLabel}>CONF</span>
        </div>
      </aside>

      <main style={ds.main}>
        <header style={ds.header}>
          <div>
            <h1 style={ds.welcomeText}>Bom dia, <span style={{fontWeight:800}}>{adminInfo.name}</span></h1>
            <p style={ds.subWelcome}>Bem-vindo de volta ao seu painel operacional.</p>
          </div>
          <div style={ds.adminProfile}>
            <div style={ds.adminInfo}>
              <p style={ds.adminName}>{adminInfo.name}</p>
              <p style={ds.adminEmail}>{adminInfo.email}</p>
            </div>
            <div style={ds.avatar}>AD</div>
          </div>
        </header>

        <div style={ds.grid}>
          <section style={ds.cardMain}>
            <h3>Faturamento Mensal</h3>
            <div style={ds.chartContainer}>
              {[40, 70, 45, 90, 60, 80, 55].map((h, i) => (
                <div key={i} style={{...ds.bar, height: `${h}%`, background: h === 90 ? '#fff' : 'rgba(255,255,255,0.3)'}}></div>
              ))}
            </div>
            <h2 style={{fontSize: '32px', margin: '15px 0 5px 0'}}>R$ 74.503,00</h2>
          </section>

          <section style={ds.cardBlack}>
            <p style={{fontSize: '11px', opacity: 0.6}}>Status da Unidade</p>
            <h4 style={{margin: '5px 0 20px 0'}}>Van Mercedes Sprinter</h4>
            <div style={{fontSize: '18px', letterSpacing: '2px'}}>**** **** 5472</div>
          </section>
        </div>
      </main>
    </div>
  );
}

const ds = {
  wrapper: { display: 'flex', height: '100vh', backgroundColor: '#ebeef1', fontFamily: 'sans-serif' },
  sidebar: { width: '85px', display: 'flex', flexDirection: 'column', alignItems: 'center', paddingTop: '30px', gap: '15px', backgroundColor: '#ebeef1' },
  logo: { fontSize: '24px', marginBottom: '20px' },
  sideIcon: { width: '60px', height: '65px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: '#828282', cursor: 'pointer', gap: '5px' },
  sideIconActive: { width: '60px', height: '65px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', backgroundColor: '#fff', borderRadius: '18px', color: '#7c3aed', boxShadow: '0 8px 15px rgba(0,0,0,0.05)', gap: '5px' },
  sideLabel: { fontSize: '9px', fontWeight: 'bold' },
  main: { flex: 1, padding: '35px', overflowY: 'auto' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '40px' },
  welcomeText: { fontSize: '28px', margin: 0, color: '#2d3436' }, // Corrigido para cinza escuro legível
  subWelcome: { fontSize: '14px', color: '#636e72', margin: '5px 0 0 0' },
  adminProfile: { display: 'flex', alignItems: 'center', gap: '15px', background: '#fff', padding: '8px 15px', borderRadius: '20px', boxShadow: '0 4px 10px rgba(0,0,0,0.03)' },
  adminInfo: { textAlign: 'right' },
  adminName: { fontSize: '14px', fontWeight: 'bold', margin: 0, color: '#2d3436' },
  adminEmail: { fontSize: '11px', color: '#b2bec3', margin: 0 },
  avatar: { width: '42px', height: '42px', borderRadius: '50%', background: '#dfe6e9', border: '2px solid #fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', color: '#7c3aed' },
  grid: { display: 'grid', gridTemplateColumns: '1.8fr 1fr', gap: '25px' },
  cardMain: { background: 'linear-gradient(135deg, #7c3aed, #db2777)', padding: '30px', borderRadius: '35px', color: '#fff' },
  chartContainer: { display: 'flex', alignItems: 'flex-end', gap: '10px', height: '100px', margin: '20px 0' },
  bar: { flex: 1, borderRadius: '4px' },
  cardBlack: { background: '#1e272e', padding: '30px', borderRadius: '35px', color: '#fff' }
};

const loginStyles = {
  wrapper: { height: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#7c3aed' },
  card: { background: '#fff', padding: '40px', borderRadius: '20px', textAlign: 'center' },
  btn: { padding: '10px 20px', cursor: 'pointer' }
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