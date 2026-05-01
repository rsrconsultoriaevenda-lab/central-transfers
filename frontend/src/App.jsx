import { useState } from 'react';
import api from '../../painel-saas/src/api.js'; // Adicione o .js explicitamente se necessário
function App() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      // Ajuste o endpoint '/login' conforme a rota criada no seu FastAPI
      const response = await api.post('/login', {
        email: email,
        password: password
      });

      setMessage('Login realizado com sucesso! Redirecionando...');
      console.log('Dados do Usuário:', response.data);
      // Aqui você salvaria o token no localStorage futuramente
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Erro ao conectar com o servidor.';
      setMessage(`Erro: ${errorMsg}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>🚐 Central Transfers</h1>
        <p style={styles.subtitle}>Gestão de Logística - Login</p>
        
        <form onSubmit={handleLogin} style={styles.form}>
          <input
            type="email"
            placeholder="Seu e-mail"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            style={styles.input}
          />
          <input
            type="password"
            placeholder="Sua senha"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={styles.input}
          />
          <button type="submit" disabled={loading} style={styles.button}>
            {loading ? 'Autenticando...' : 'Entrar'}
          </button>
        </form>

        {message && (
          <p style={{ 
            marginTop: '15px', 
            color: message.includes('Erro') ? '#ff4d4d' : '#4caf50' 
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
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    height: '100vh',
    backgroundColor: '#121212',
    color: '#fff',
    fontFamily: 'Arial, sans-serif'
  },
  card: {
    padding: '40px',
    borderRadius: '12px',
    backgroundColor: '#1e1e1e',
    boxShadow: '0 8px 24px rgba(0,0,0,0.3)',
    textAlign: 'center',
    width: '350px'
  },
  title: { margin: '0 0 10px 0', fontSize: '24px' },
  subtitle: { color: '#888', marginBottom: '20px' },
  form: { display: 'flex', flexDirection: 'column', gap: '15px' },
  input: {
    padding: '12px',
    borderRadius: '6px',
    border: '1px solid #333',
    backgroundColor: '#2a2a2a',
    color: '#fff',
    fontSize: '16px'
  },
  button: {
    padding: '12px',
    borderRadius: '6px',
    border: 'none',
    backgroundColor: '#007bff',
    color: '#fff',
    fontSize: '16px',
    cursor: 'pointer',
    fontWeight: 'bold'
  }
};

export default App;