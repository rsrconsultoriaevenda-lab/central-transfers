import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Login() {
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
        @keyframes gradientBG {
          0% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }
        @keyframes vanTravel {
          from { left: -150px; }
          to { left: 100%; }
        }
        .fleet-bg {
          mask-image: linear-gradient(to top, transparent, black, transparent);
          -webkit-mask-image: linear-gradient(to top, transparent, black, transparent);
        }
      `}</style>

      {/* Camada 1: Imagem de Gramado (Overlay Suave) */}
      <div style={loginStyles.cityOverlay}></div>

      {/* Camada 2: Frota de Carros (Spin, Van, Cruze) ao Fundo */}
      <div style={loginStyles.fleetContainer} className="fleet-bg">
        <div style={loginStyles.vehicleEmbossed}>
          <div style={loginStyles.vLabel}>CRUZE</div>
          <span style={loginStyles.vIcon}>🚗</span>
        </div>
        <div style={{...loginStyles.vehicleEmbossed, transform: 'scale(1.3) translateY(-20px)'}}>
          <div style={loginStyles.vLabel}>VAN EXEC</div>
          <span style={loginStyles.vIcon}>🚐</span>
        </div>
        <div style={loginStyles.vehicleEmbossed}>
          <div style={loginStyles.vLabel}>SPIN 7L</div>
          <span style={loginStyles.vIcon}>🚘</span>
        </div>
      </div>

      {/* Camada 3: Card de Login Glassmorphism */}
      <div style={loginStyles.glassCard}>
        <div style={loginStyles.logoContainer}>
          <div style={loginStyles.iconCircle}>🚐</div>
          <h1 style={loginStyles.title}>Central Transfers</h1>
          <p style={loginStyles.subtitle}>Sua conexão premium em Gramado</p>
        </div>

        <form onSubmit={handleLogin} style={loginStyles.form}>
          <div style={loginStyles.inputGroup}>
            <label style={loginStyles.label}>Usuário ou E-mail</label>
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
            <label style={loginStyles.label}>Senha de Acesso</label>
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
            Acessar Sistema
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

// --- DESIGN SYSTEM (ESTILOS) ---
const loginStyles = {
  pageWrapper: {
    height: '100vh',
    width: '100vw',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    background: 'linear-gradient(-45deg, #1e1b4b, #4c1d95, #7c3aed, #1e1b4b)',
    backgroundSize: '400% 400%',
    animation: 'gradientBG 12s ease infinite',
    fontFamily: '"Inter", sans-serif',
    overflow: 'hidden',
    position: 'relative'
  },
  cityOverlay: {
    position: 'absolute',
    top: 0, left: 0, right: 0, bottom: 0,
    // URL de Gramado (Exemplo: Pórtico) com opacidade baixa
    backgroundImage: 'url("https://images.unsplash.com/photo-1626014903708-3607062400f0?q=80&w=2000")', 
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    opacity: 0.15,
    mixBlendMode: 'overlay'
  },
  fleetContainer: {
    position: 'absolute',
    width: '100%',
    top: '20%',
    display: 'flex',
    justifyContent: 'space-around',
    alignItems: 'center',
    padding: '0 5%',
    zIndex: 1,
    userSelect: 'none'
  },
  vehicleEmbossed: {
    textAlign: 'center',
    filter: 'drop-shadow(0 10px 10px rgba(0,0,0,0.5))',
    transition: 'transform 0.5s'
  },
  vIcon: {
    fontSize: '120px',
    display: 'block', // Garante que o ícone ocupe o espaço correto
    background: 'linear-gradient(135deg, #7c3aed 0%, #4c1d95 100%)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    filter: 'drop-shadow(2px 2px 0px rgba(255,255,255,0.1))'
  },
  vLabel: {
    fontSize: '24px',
    fontWeight: '900',
    color: 'rgba(76, 29, 149, 0.8)',
    textShadow: '1px 1px 2px rgba(255,255,255,0.2), -1px -1px 2px rgba(0,0,0,0.5)',
    marginBottom: '-20px'
  },
  
  glassCard: {
    background: 'rgba(255, 255, 255, 0.05)',
    backdropFilter: 'blur(25px) saturate(180%)',
    WebkitBackdropFilter: 'blur(25px)',
    borderRadius: '40px',
    padding: '60px 45px',
    width: '100%',
    maxWidth: '400px',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    boxShadow: '0 40px 100px rgba(0,0,0,0.4)',
    textAlign: 'center',
    zIndex: 10
  },
  iconCircle: {
    width: '80px', height: '80px',
    backgroundColor: 'rgba(255,255,255,0.1)',
    borderRadius: '50%',
    display: 'flex', justifyContent: 'center', alignItems: 'center',
    fontSize: '40px', margin: '0 auto 20px'
  },
  title: { color: '#fff', fontSize: '32px', fontWeight: 'bold', margin: '0 0 8px 0' },
  subtitle: { color: 'rgba(255,255,255,0.6)', fontSize: '15px', marginBottom: '40px' },
  input: {
    width: '100%',
    padding: '16px',
    borderRadius: '16px',
    border: '1px solid rgba(255,255,255,0.1)',
    backgroundColor: 'rgba(0,0,0,0.3)',
    color: '#fff',
    marginBottom: '20px',
    outline: 'none',
    boxSizing: 'border-box'
  },
  label: { color: 'rgba(255,255,255,0.8)', fontSize: '13px', marginBottom: '8px', display: 'block', textAlign: 'left', marginLeft: '5px' },
  button: {
    width: '100%',
    padding: '18px',
    borderRadius: '18px',
    border: 'none',
    background: '#fff',
    color: '#4c1d95',
    fontWeight: 'bold',
    fontSize: '16px',
    cursor: 'pointer',
    boxShadow: '0 15px 30px rgba(0,0,0,0.2)',
    transition: 'all 0.3s'
  },
  roadLine: { position: 'absolute', bottom: '60px', width: '100%', height: '1px', background: 'rgba(255,255,255,0.1)' },
  animatedVan: { position: 'absolute', bottom: '5px', fontSize: '35px', animation: 'vanTravel 12s linear infinite' }
};