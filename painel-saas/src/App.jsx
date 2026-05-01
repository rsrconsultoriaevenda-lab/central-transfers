import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate, Navigate } from 'react-router-dom';

/**
 * COMPONENTE: LOGIN
 * Corrigido para aceitar digitação e navegar corretamente
 */
function Login() {
  const navigate = useNavigate();
  
  // Estados para os inputs (isso libera a digitação)
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = (e) => {
    e.preventDefault(); // Impede o recarregamento da página
    
    // Simulação de validação simples
    if (email !== "" && password !== "") {
      console.log("Autenticando...", { email, password });
      navigate('/dashboard'); // Direciona para o Dashboard
    } else {
      alert("Por favor, preencha todos os campos.");
    }
  };

  return (
    <div style={loginStyles.container}>
      <div style={loginStyles.card}>
        <div style={styles.logoBadge}>🚐</div>
        <h1 style={loginStyles.title}>Central Transfers</h1>
        <p style={loginStyles.subtitle}>Gestão de logística para Gramado e Região</p>
        
        <form onSubmit={handleLogin} style={loginStyles.form}>
          <div style={loginStyles.inputGroup}>
            <label style={loginStyles.label}>E-mail</label>
            <input 
              type="email" 
              placeholder="admin@centraltransfers.com" 
              style={loginStyles.input} 
              value={email}
              onChange={(e) => setEmail(e.target.value)} // Atualiza o estado ao digitar
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
              onChange={(e) => setPassword(e.target.value)} // Atualiza o estado ao digitar
              required
            />
          </div>
          <button type="submit" style={loginStyles.button}>
            Entrar no Painel
          </button>
        </form>
      </div>
    </div>
  );
}

/**
 * COMPONENTE: DASHBOARD
 */
function Dashboard() {
  const navigate = useNavigate();

  return (
    <div style={styles.appContainer}>
      {/* Sidebar */}
      <aside style={styles.sidebar}>
        <div style={styles.logoBadge}>🚐</div>
        <div style={styles.iconMenu}>
          <div style={{...styles.iconWrapper, ...styles.iconActive}}>📊</div>
          <div style={styles.iconWrapper}>🚘</div>
          <div style={styles.iconWrapper} onClick={() => navigate('/login')}>🚪</div> {/* Botão Sair */}
        </div>
      </aside>

      <main style={styles.mainContent}>
        <header style={styles.header}>
          <div style={styles.navTabs}>
            {['Visão Geral', 'Reservas', 'Motoristas'].map((tab) => (
              <button key={tab} style={tab === 'Visão Geral' ? styles.tabActive : styles.tab}>{tab}</button>
            ))}
          </div>
          <button onClick={() => navigate('/login')} style={{...styles.tab, color: '#ef4444'}}>Sair</button>
        </header>

        <section style={styles.greetingSection}>
          <h1 style={styles.greetingTitle}>Bom dia, Admin</h1>
          <p style={styles.greetingSubtitle}>Você tem 12 transfers pendentes hoje.</p>
        </section>

        <div style={styles.dashboardGrid}>
          <div style={styles.leftColumn}>
            <div style={styles.cardLarge}>
              <h3 style={styles.cardTitle}>Volume de Passageiros</h3>
              <div style={styles.chartArea}>
                <div style={styles.barGroup}>
                  <div style={{...styles.bar, height: '60%', ...styles.chromaticBar}}></div>
                  <div style={{...styles.bar, height: '90%', ...styles.chromaticBar}}></div>
                  <div style={{...styles.bar, height: '40%', ...styles.chromaticBar}}></div>
                </div>
              </div>
            </div>
          </div>
          
          <div style={styles.rightColumn}>
            <div style={styles.cardChromatic}>
              <h4 style={styles.chromaticTitle}>Faturamento</h4>
              <h2 style={styles.chromaticValue}>R$ 14.500</h2>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

/**
 * COMPONENTE PRINCIPAL
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

// --- ESTILOS (IGUAIS AO ANTERIOR, COM AJUSTES DE CLIQUE) ---
const loginStyles = {
  container: { height: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center', backgroundColor: '#f5f5f7', fontFamily: 'sans-serif' },
  card: { backgroundColor: '#fff', padding: '40px', borderRadius: '24px', boxShadow: '0 10px 40px rgba(0,0,0,0.05)', width: '350px', textAlign: 'center' },
  title: { fontSize: '22px', marginBottom: '10px' },
  subtitle: { fontSize: '14px', color: '#666', marginBottom: '25px' },
  form: { textAlign: 'left' },
  inputGroup: { marginBottom: '15px' },
  label: { display: 'block', fontSize: '13px', fontWeight: '600', marginBottom: '5px' },
  input: { width: '100%', padding: '12px', borderRadius: '10px', border: '1px solid #ddd', boxSizing: 'border-box' },
  button: { width: '100%', padding: '12px', borderRadius: '10px', border: 'none', background: 'linear-gradient(135deg, #8b5cf6, #d946ef)', color: '#fff', fontWeight: 'bold', cursor: 'pointer', marginTop: '10px' }
};

const styles = {
  appContainer: { display: 'flex', minHeight: '100vh', backgroundColor: '#f5f5f7', fontFamily: 'sans-serif' },
  sidebar: { width: '80px', backgroundColor: '#fff', borderRight: '1px solid #eee', display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '20px 0' },
  logoBadge: { fontSize: '24px', marginBottom: '30px' },
  iconMenu: { display: 'flex', flexDirection: 'column', gap: '20px' },
  iconWrapper: { width: '40px', height: '40px', display: 'flex', justifyContent: 'center', alignItems: 'center', borderRadius: '50%', cursor: 'pointer' },
  iconActive: { backgroundColor: '#f3e8ff', color: '#a855f7' },
  mainContent: { flex: 1, padding: '30px' },
  header: { display: 'flex', justifyContent: 'space-between', marginBottom: '30px' },
  navTabs: { display: 'flex', gap: '10px' },
  tab: { padding: '8px 16px', border: 'none', backgroundColor: 'transparent', cursor: 'pointer', fontWeight: '600' },
  tabActive: { padding: '8px 16px', backgroundColor: '#333', color: '#fff', borderRadius: '20px' },
  greetingSection: { marginBottom: '30px' },
  greetingTitle: { fontSize: '28px', margin: 0 },
  greetingSubtitle: { color: '#666' },
  dashboardGrid: { display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '20px' },
  cardLarge: { backgroundColor: '#fff', padding: '20px', borderRadius: '20px' },
  cardTitle: { fontSize: '16px', margin: '0 0 20px 0' },
  chartArea: { height: '150px', display: 'flex', alignItems: 'flex-end', gap: '10px' },
  barGroup: { display: 'flex', gap: '10px', width: '100%', alignItems: 'flex-end' },
  bar: { flex: 1, borderRadius: '5px' },
  chromaticBar: { background: 'linear-gradient(to top, #8b5cf6, #d946ef)' },
  cardChromatic: { background: 'linear-gradient(135deg, #8b5cf6, #d946ef)', padding: '20px', borderRadius: '20px', color: '#fff' },
  chromaticTitle: { margin: 0, opacity: 0.8 },
  chromaticValue: { fontSize: '32px', margin: '10px 0' }
};