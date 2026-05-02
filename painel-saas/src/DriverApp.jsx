import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8001';

export default function DriverApp() {
  const [myOrders, setMyOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  const getAuthHeader = () => {
    const token = localStorage.getItem('token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  const loadMyOrders = async () => {
    setLoading(true);
    try {
      // O backend já filtra pelo motorista logado graças ao nosso middleware de tenant
      const res = await axios.get(`${API_URL}/pedidos`, { headers: getAuthHeader() });
      // Filtramos no front apenas para garantir exibição de ordens aceitas ou concluídas no dia
      setMyOrders(res.data.filter(p => p.status !== 'CANCELADO'));
    } catch (err) {
      console.error("Erro ao carregar ordens do motorista", err);
    } finally {
      setLoading(false);
    }
  };

  const updateStatus = async (pedidoId, newStatus) => {
    try {
      await axios.put(`${API_URL}/pedidos/${pedidoId}/status`, { status: newStatus }, { headers: getAuthHeader() });
      loadMyOrders();
    } catch (err) {
      alert("Erro ao atualizar status");
    }
  };

  useEffect(() => { loadMyOrders(); }, []);

  return (
    <div style={styles.container}>
      <nav style={styles.nav}>
        <h3>Minha Agenda 🚖</h3>
        <button onClick={loadMyOrders} style={styles.refreshBtn}>🔄</button>
      </nav>

      {loading ? <p>Carregando serviços...</p> : (
        <div style={styles.list}>
          {myOrders.length === 0 && <p>Nenhum serviço atribuído para hoje.</p>}
          {myOrders.map(order => (
            <div key={order.id} style={styles.card}>
              <div style={styles.header}>
                <span style={styles.id}># {order.id}</span>
                <span style={{...styles.status, backgroundColor: order.status === 'CONCLUIDO' ? '#dcfce7' : '#fef3c7'}}>
                  {order.status}
                </span>
              </div>
              <div style={styles.info}>
                <p>📍 <strong>Origem:</strong> {order.origem}</p>
                <p>🏁 <strong>Destino:</strong> {order.destino}</p>
                <p>⏰ <strong>Horário:</strong> {new Date(order.data_servico).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</p>
              </div>
              
              {order.status === 'ACEITO' && (
                <button onClick={() => updateStatus(order.id, 'CONCLUIDO')} style={styles.btnFinish}>
                  Finalizar Corrida ✅
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

const styles = {
  container: { background: '#f1f5f9', minHeight: '100vh', padding: '15px', fontFamily: 'sans-serif' },
  nav: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' },
  refreshBtn: { background: '#fff', border: '1px solid #ddd', padding: '10px', borderRadius: '10px' },
  list: { display: 'flex', flexDirection: 'column', gap: '15px' },
  card: { background: '#fff', borderRadius: '15px', padding: '15px', boxShadow: '0 4px 6px rgba(0,0,0,0.05)' },
  header: { display: 'flex', justifyContent: 'space-between', marginBottom: '10px' },
  id: { fontWeight: 'bold', color: '#64748b' },
  status: { fontSize: '12px', padding: '4px 8px', borderRadius: '8px', fontWeight: 'bold' },
  info: { fontSize: '14px', color: '#1e293b', marginBottom: '15px' },
  btnFinish: { width: '100%', padding: '15px', background: '#4c1d95', color: '#fff', border: 'none', borderRadius: '12px', fontWeight: 'bold', fontSize: '16px' }
};