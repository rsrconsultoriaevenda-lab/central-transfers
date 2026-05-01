import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate, Navigate } from 'react-router-dom';

/**
 * COMPONENTE: LOGIN (VERSÃO CROMÁTICA PREMIUM)
 */
function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = (e) => {
    e.preventDefault();
    if (email && password) {
      navigate('/dashboard');
    }
  };

  return (
    <div style={loginStyles.pageWrapper}>
      {/* Estilos Globais de Animação via tag style */}
      <style>{`
        @keyframes gradientBG {
          0% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }
        @keyframes vanTravel {
          from { left: -100px; }
          to { left: 100%; }
        }
        input::placeholder { color: rgba(255,255,255,0.4); }
      `}</style>

      {/* Cartão de Login */}
      <div style={loginStyles.glassCard}>
        <div style={loginStyles.logoContainer}>
          <span style={loginStyles.vanEmoji}>🚐</span>
          <h1 style={loginStyles.title}>Central Transfers</h1>
          <p style={loginStyles.subtitle}>Logística Inteligente para Gramado</p>
        </div>

        <form onSubmit={handleLogin} style={loginStyles.form}>
          <div style={loginStyles.inputGroup}>
            <label style={loginStyles.label}>E-mail de acesso</label>
            <input 
              type="email" 
              placeholder="admin@centraltransfers.com" 
              style={loginStyles.input}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div style={loginStyles.inputGroup}>
            <label style={loginStyles.label}>Senha</label>
            <input 
              type="password" 
              placeholder="••••••••" 
              style={loginStyles.input}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <button type="submit" style={loginStyles.button}>
            Entrar no Painel
          </button>
        </form>
      </div>

      {/* Animação da Van no Rodapé */}
      <div style={loginStyles.roadLine}>
        <div style={loginStyles.animatedVan}>🚐💨</div>
      </div>
    </div>
  );
}

/**
 * COMPONENTE: DASHBOARD (MANTIDO E INTEGRADO)
 */
function Dashboard() {
  const navigate = useNavigate();
  return (
    <div style={styles.appContainer}>
      <aside style={styles.sidebar}>
        <div style={styles.logoBadge}>🚐</div>
        <div style={styles.iconMenu}>
          <div style={{...styles.iconWrapper, ...styles.iconActive}}>📊</div>
          <div style={styles.iconWrapper} onClick={() => navigate('/login')}>🚪</div>
        </div>
      </aside>
      <main style={styles.mainContent}>
        <h1 style={styles.greetingTitle}>Dashboard Ativo</h1>
        <p>Bem-vindo ao sistema de logística.</p>
        <div style={styles.cardChromatic}>
           <h2 style={styles.chromaticValue}>R$ 14.500,00</h2>
           <p>Faturamento Previsto</p>
        </div>
      </main>
    </div>
  );
}

/**
 * APP PRINCIPAL
 */
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

// --- ESTILOS DE LOGIN (CROMÁTICO ROXO) ---
const loginStyles = {
  pageWrapper: {
    height: '100vh',
    width: '100vw',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    background: 'linear-gradient(-45deg, #4c1d95, #7c3aed, #db2777, #2563eb)',
    backgroundSize: '400% 400%',
    animation: 'gradientBG 15s ease infinite',
    fontFamily: '"Inter", sans-serif',
    overflow: 'hidden',
    position: 'relative'
  },
  glassCard: {
    background: 'rgba(255, 255, 255, 0.1)',
    backdropFilter: 'blur(15px)',
    WebkitBackdropFilter: 'blur(15px)',
    borderRadius: '30px',
    padding: '50px 40px',
    width: '100%',
    maxWidth: '420px',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    boxShadow: '0 25px 50px rgba(0,0,0,0.3)',
    textAlign: 'center',
    zIndex: 10
  },
  title: { color: '#fff', fontSize: '28px', fontWeight: '800', margin: '15px 0 5px 0', letterSpacing: '-0.5px' },
  subtitle: { color: 'rgba(255,255,255,0.7)', fontSize: '14px', marginBottom: '35px' },
  vanEmoji: { fontSize: '50px', display: 'block' },
  form: { textAlign: 'left' },
  inputGroup: { marginBottom: '20px' },
  label: { color: '#fff', fontSize: '13px', fontWeight: '500', marginBottom: '8px', display: 'block', opacity: 0.9 },
  input: {
    width: '100%',
    padding: '14px 18px',
    borderRadius: '15px',
    border: '1px solid rgba(255,255,255,0.2)',
    backgroundColor: 'rgba(0,0,0,0.2)',
    color: '#fff',
    fontSize: '15px',
    outline: 'none',
    boxSizing: 'border-box',
    transition: 'all 0.3s'
  },
  button: {
    width: '100%',
    padding: '16px',
    borderRadius: '15px',
    border: 'none',
    background: '#fff',
    color: '#7c3aed',
    fontWeight: '800',
    fontSize: '16px',
    cursor: 'pointer',
    marginTop: '15px',
    boxShadow: '0 10px 25px rgba(0,0,0,0.2)',
    transition: 'transform 0.2s'
  },
  roadLine: {
    position: 'absolute',
    bottom: '40px',
    width: '100%',
    height: '2px',
    background: 'rgba(255,255,255,0.2)',
    zIndex: 1
  },
  animatedVan: {
    position: 'absolute',
    bottom: '5px',
    fontSize: '30px',
    animation: 'vanTravel 10s linear infinite',
  }
};

// --- ESTILOS DASHBOARD (BÁSICO PARA EXEMPLO) ---
const styles = {
  appContainer: { display: 'flex', minHeight: '100vh', backgroundColor: '#f8fafc' },
  sidebar: { width: '80px', backgroundColor: '#fff', display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '20px 0', borderRight: '1px solid #e2e8f0' },
  logoBadge: { fontSize: '24px', marginBottom: '30px' },
  iconMenu: { display: 'flex', flexDirection: 'column', gap: '20px' },
  iconWrapper: { width: '45px', height: '45px', display: 'flex', justifyContent: 'center', alignItems: 'center', borderRadius: '12px', cursor: 'pointer' },
  iconActive: { backgroundColor: '#f3e8ff', color: '#7c3aed' },
  mainContent: { flex: 1, padding: '40px' },
  greetingTitle: { fontSize: '32px', fontWeight: 'bold' },
  cardChromatic: { 
    background: 'linear-gradient(135deg, #7c3aed, #db2777)', 
    padding: '30px', 
    borderRadius: '24px', 
    color: '#fff', 
    marginTop: '20px',
    maxWidth: '300px'
  },
  chromaticValue: { fontSize: '36px', fontWeight: 'bold', margin: 0 }
};