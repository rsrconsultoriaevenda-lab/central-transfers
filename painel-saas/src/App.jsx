import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate, Navigate } from 'react-router-dom';

// --- ÍCONES ESTILO SOLID (Mais destaque) ---
const Icons = {
  Home: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/></svg>,
  Stats: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M5 9.2h3V19H5zM10.6 5h2.8V19h-2.8zm5.6 8H19v6h-2.8z"/></svg>,
  User: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>,
  Settings: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.09.63-.09.94s.02.64.07.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/></svg>,
};

// --- TELA DE LOGIN (ESTILO GRAMADO) ---
function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = (e) => {
    e.preventDefault();
    if (email && password) navigate('/dashboard');
  };

  return (
    <div style={loginStyles.wrapper}>
      <style>{`
        @keyframes grad { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
        @keyframes van { from { left: -150px; } to { left: 100%; } }
      `}</style>
      <div style={loginStyles.cityBg}></div>
      <div style={loginStyles.card}>
        <div style={loginStyles.icon}>🚐</div>
        <h2>Central Transfers</h2>
        <p>Acesse seu painel logístico</p>
        <form onSubmit={handleLogin}>
          <input type="email" placeholder="E-mail" style={loginStyles.input} onChange={e => setEmail(e.target.value)} required />
          <input type="password" placeholder="Senha" style={loginStyles.input} onChange={e => setPassword(e.target.value)} required />
          <button type="submit" style={loginStyles.btn}>Entrar no Sistema</button>
        </form>
      </div>
      <div style={loginStyles.road}><div style={loginStyles.van}>🚐💨</div></div>
    </div>
  );
}

// --- DASHBOARD (ESTILO NEXTPAY / DISRUPTIVO) ---
function Dashboard() {
  const navigate = useNavigate();
  const [tab, setTab] = useState('Home');

  return (
    <div style={ds.wrapper}>
      <aside style={ds.sidebar}>
        <div onClick={() => setTab('Home')} style={tab === 'Home' ? ds.sideIconActive : ds.sideIcon}><Icons.Home /></div>
        <div onClick={() => setTab('Stats')} style={tab === 'Stats' ? ds.sideIconActive : ds.sideIcon}><Icons.Stats /></div>
        <div onClick={() => setTab('User')} style={tab === 'User' ? ds.sideIconActive : ds.sideIcon}><Icons.User /></div>
        <div onClick={() => navigate('/login')} style={ds.sideIcon}><Icons.Settings /></div>
      </aside>

      <main style={ds.main}>
        <header style={ds.header}>
          <div>
            <h1 style={{fontSize: '24px', margin: 0}}>Bom dia, <span style={{fontWeight:800}}>Admin</span></h1>
            <p style={{fontSize: '13px', color: '#e11d48', margin: '5px 0 0 0'}}>● 5 transfers pendentes para hoje</p>
          </div>
          <div style={{display:'flex', gap:'15px', alignItems:'center'}}>
            <button style={ds.btnTop}>+ Novo Serviço</button>
            <div style={ds.avatar}>AD</div>
          </div>
        </header>

        <div style={ds.grid}>
          {/* Card Principal Cromático */}
          <section style={ds.cardMain}>
            <div style={{display:'flex', justifyContent:'space-between'}}>
              <h3>Faturamento</h3>
              <span style={{fontSize:'12px', fontWeight:'bold'}}>ESTA SEMANA</span>
            </div>
            <div style={ds.chartContainer}>
              {[40, 70, 45, 90, 60, 80, 55].map((h, i) => (
                <div key={i} style={{...ds.bar, height: `${h}%`, background: h === 90 ? '#fff' : 'rgba(255,255,255,0.3)'}}></div>
              ))}
            </div>
            <h2 style={{fontSize: '32px', margin: '15px 0 5px 0'}}>R$ 74.503,00</h2>
            <p style={{fontSize: '13px', opacity: 0.8}}>↑ 13% em relação ao mês anterior</p>
          </section>

          {/* Card Frota (Preto) */}
          <section style={ds.cardBlack}>
            <p style={{fontSize: '11px', opacity: 0.6, margin: 0}}>Frota Ativa</p>
            <h4 style={{margin: '5px 0 20px 0'}}>Van Mercedes Sprinter</h4>
            <div style={{fontSize: '18px', letterSpacing: '3px', marginBottom: '20px'}}>**** **** 5472</div>
            <div style={{display:'flex', justifyContent:'space-between', fontSize:'12px'}}>
              <span>ID: 8892-XP</span>
              <span style={{color:'#10b981'}}>DISPONÍVEL</span>
            </div>
          </section>

          {/* Atividades Recentes */}
          <section style={ds.cardWhite}>
            <h4 style={{margin: '0 0 20px 0'}}>Atividades Recentes</h4>
            {[
              { label: 'Transfer Gramado', user: 'Ricardo S.', price: '250', icon: '🚐' },
              { label: 'Tour Vinhedos', user: 'Ana Paula', price: '480', icon: '🍷' },
              { label: 'PoA Airport', user: 'Marcos V.', price: '320', icon: '🛫' }
            ].map((item, i) => (
              <div key={i} style={ds.row}>
                <div style={ds.rowIcon}>{item.icon}</div>
                <div style={{flex: 1, fontSize:'13px'}}><strong>{item.label}</strong><br/><small style={{color:'#888'}}>{item.user}</small></div>
                <div style={{fontWeight:'bold', color:'#10b981'}}>R$ {item.price}</div>
              </div>
            ))}
          </section>

          {/* Upgrade / Alerta */}
          <section style={ds.cardYellow}>
            <h4>Otimização</h4>
            <p style={{fontSize:'13px'}}>Sua frota atingiu 85% da capacidade semanal.</p>
            <button style={ds.btnYellow}>Ver Relatórios</button>
          </section>
        </div>
      </main>
    </div>
  );
}

// --- ESTILOS LOGIN ---
const loginStyles = {
  wrapper: { height: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center', background: 'linear-gradient(-45deg, #1e1b4b, #4c1d95, #7c3aed, #1e1b4b)', backgroundSize: '400% 400%', animation: 'grad 12s ease infinite', position: 'relative', overflow: 'hidden', fontFamily: 'sans-serif' },
  cityBg: { position: 'absolute', inset: 0, backgroundImage: 'url("https://images.unsplash.com/photo-1626014903708-3607062400f0?q=80&w=2000")', backgroundSize: 'cover', opacity: 0.1, mixBlendMode: 'overlay' },
  card: { background: 'rgba(255, 255, 255, 0.1)', backdropFilter: 'blur(20px)', padding: '50px', borderRadius: '35px', width: '380px', textAlign: 'center', border: '1px solid rgba(255,255,255,0.2)', zIndex: 10, color: '#fff' },
  icon: { fontSize: '40px', marginBottom: '15px' },
  input: { width: '100%', padding: '15px', marginBottom: '15px', borderRadius: '15px', border: 'none', background: 'rgba(0,0,0,0.3)', color: '#fff', boxSizing: 'border-box' },
  btn: { width: '100%', padding: '15px', borderRadius: '15px', border: 'none', background: '#fff', color: '#4c1d95', fontWeight: 'bold', cursor: 'pointer' },
  road: { position: 'absolute', bottom: '60px', width: '100%', height: '1px', background: 'rgba(255,255,255,0.1)' },
  van: { position: 'absolute', bottom: '5px', fontSize: '30px', animation: 'van 15s linear infinite' }
};

// --- ESTILOS DASHBOARD (STILO NEXTPAY) ---
const ds = {
  wrapper: { display: 'flex', height: '100vh', backgroundColor: '#e2e4e7', fontFamily: 'sans-serif' },
  sidebar: { width: '80px', display: 'flex', flexDirection: 'column', alignItems: 'center', paddingTop: '40px', gap: '20px' },
  sideIcon: { width: '45px', height: '45px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#94a3b8', cursor: 'pointer' },
  sideIconActive: { width: '45px', height: '45px', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#fff', borderRadius: '15px', color: '#7c3aed', boxShadow: '0 10px 20px rgba(0,0,0,0.05)' },
  main: { flex: 1, padding: '30px', overflowY: 'auto' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' },
  btnTop: { padding: '12px 20px', borderRadius: '15px', border: 'none', backgroundColor: '#000', color: '#fff', fontWeight: 'bold', cursor: 'pointer' },
  avatar: { width: '45px', height: '45px', borderRadius: '50%', backgroundColor: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', border: '2px solid #ccc' },
  grid: { display: 'grid', gridTemplateColumns: '1.8fr 1fr', gap: '25px' },
  cardMain: { background: 'linear-gradient(135deg, #7c3aed, #db2777)', padding: '30px', borderRadius: '35px', color: '#fff', boxShadow: '0 20px 40px rgba(124,58,237,0.2)' },
  chartContainer: { display: 'flex', alignItems: 'flex-end', gap: '10px', height: '120px', margin: '20px 0' },
  bar: { flex: 1, borderRadius: '5px' },
  cardBlack: { background: 'linear-gradient(to bottom, #444, #000)', padding: '30px', borderRadius: '35px', color: '#fff' },
  cardWhite: { background: '#fff', padding: '30px', borderRadius: '35px' },
  row: { display: 'flex', alignItems: 'center', gap: '15px', padding: '15px 0', borderBottom: '1px solid #f0f0f0' },
  rowIcon: { width: '40px', height: '40px', backgroundColor: '#f8fafc', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center' },
  cardYellow: { background: 'linear-gradient(135deg, #fbbf24, #f59e0b)', padding: '30px', borderRadius: '35px', color: '#fff' },
  btnYellow: { width: '100%', padding: '12px', borderRadius: '15px', border: 'none', background: 'rgba(255,255,255,0.2)', color: '#fff', fontWeight: 'bold', marginTop: '10px', cursor: 'pointer' }
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