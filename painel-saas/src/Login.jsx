import { useState } from 'react';
import api from './api';

function Login({ onLoginSuccess }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [status, setStatus] = useState('idle'); // idle, loading, success, error
  const [message, setMessage] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    setStatus('loading'); // A van chega!
    setMessage('');

    try {
      // Simulando a chamada da API (Substitua pela sua rota real)
      const response = await api.post('/login', { email, password });
      
      setStatus('success'); // A van sai!
      setMessage('Acesso autorizado! Boa viagem.');
      
      // Espera a animação da van sair da tela para mudar de página
      setTimeout(() => {
        onLoginSuccess(response.data);
      }, 1500);

    } catch (error) {
      setStatus('error');
      setMessage('Ops! Verifique suas credenciais.');
      // Volta ao estado normal após o erro para tentar de novo
      setTimeout(() => setStatus('idle'), 2000);
    }
  };

  return (
    <div style={styles.container}>
      {/* Estrada/Pista por onde a van passa */}
      <div style={styles.road}>
        <div style={{
          ...styles.van,
          ...(status === 'loading' ? styles.vanArriving : {}),
          ...(status === 'success' ? styles.vanDeparting : {})
        }}>
          🚐
          <div style={styles.vanLight}></div>
        </div>
      </div>

      <div style={styles.loginCard}>
        <h1 style={styles.title}>Central Transfers</h1>
        <p style={styles.subtitle}>Gestão de Logística</p>

        <form onSubmit={handleLogin} style={styles.form}>
          <input
            type="email"
            placeholder="E-mail"
            style={styles.input}
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Senha"
            style={styles.input}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button 
            type="submit" 
            disabled={status === 'loading' || status === 'success'}
            style={status === 'success' ? styles.buttonSuccess : styles.button}
          >
            {status === 'loading' ? 'Autenticando...' : 
             status === 'success' ? 'Sucesso!' : 'Entrar'}
          </button>
        </form>

        {message && (
          <p style={{ 
            marginTop: '20px', 
            color: status === 'error' ? '#ef4444' : '#a855f7',
            fontWeight: '500'
          }}>
            {message}
          </p>
        )}
      </div>
    </div>
  );
}

const styles = {
  container: {
    height: '100vh',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f7',
    overflow: 'hidden',
    fontFamily: '"Inter", sans-serif',
  },
  road: {
    width: '100%',
    height: '60px',
    position: 'relative',
    marginBottom: '20px',
  },
  van: {
    fontSize: '50px',
    position: 'absolute',
    left: '-100px', // Começa fora da tela à esquerda
    transition: 'all 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
    zIndex: 10,
  },
  vanArriving: {
    left: 'calc(50% - 25px)', // Para no meio da tela (em cima do card)
  },
  vanDeparting: {
    left: '110vw', // Sai pela direita
    transition: 'all 1s ease-in',
  },
  loginCard: {
    backgroundColor: 'rgba(255, 255, 255, 0.8)',
    backdropFilter: 'blur(10px)',
    padding: '50px',
    borderRadius: '30px',
    boxShadow: '0 20px 40px rgba(0,0,0,0.05)',
    width: '380px',
    textAlign: 'center',
    border: '1px solid rgba(255,255,255,0.3)',
  },
  title: { fontSize: '28px', margin: '0 0 5px 0', fontWeight: '700' },
  subtitle: { color: '#888', marginBottom: '30px' },
  form: { display: 'flex', flexDirection: 'column', gap: '15px' },
  input: {
    padding: '15px 20px',
    borderRadius: '15px',
    border: '1px solid #eee',
    backgroundColor: '#fff',
    outline: 'none',
    fontSize: '16px',
  },
  button: {
    padding: '15px',
    borderRadius: '15px',
    border: 'none',
    background: 'linear-gradient(135deg, #8b5cf6 0%, #d946ef 100%)',
    color: '#fff',
    fontWeight: 'bold',
    fontSize: '16px',
    cursor: 'pointer',
    boxShadow: '0 10px 20px rgba(168, 85, 247, 0.2)',
    transition: 'transform 0.2s',
  },
  buttonSuccess: {
    padding: '15px',
    borderRadius: '15px',
    border: 'none',
    backgroundColor: '#10b981',
    color: '#fff',
    fontWeight: 'bold',
    fontSize: '16px',
  }
};

export default Login;