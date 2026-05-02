import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8001';

export default function Storefront() {
  const [services, setServices] = useState([]);
  const [cart, setCart] = useState([]);
  const [category, setCategory] = useState('TRANSFERS'); 
  const [bookingData, setBookingData] = useState({
    origem: '',
    destino: '',
    data: '',
    hora: '',
    passageiros: 1
  });
  const [step, setStep] = useState('catalog'); // catalog, details, success

  useEffect(() => {
    // Busca serviços cadastrados no seu backend
    axios.get(`${API_URL}/servicos`).then(res => setServices(res.data));
  }, []);

  const addToCart = (service) => {
    setCart([service]); // Para o MVP, focamos em um serviço por vez
    setStep('details');
  };

  const handleCheckout = () => {
    const resumo = `*Reserva Central Transfers*\n\n` +
      `📋 Serviço: ${cart[0].nome}\n` +
      `📍 De: ${bookingData.origem}\n` +
      `🏁 Para: ${bookingData.destino}\n` +
      `📅 Data: ${bookingData.data} às ${bookingData.hora}\n` +
      `👥 Passageiros: ${bookingData.passageiros}`;
    
    window.location.href = `https://wa.me/5554999999999?text=${encodeURIComponent(resumo)}`;
  };

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <h1>Central Transfers & Experiences</h1>
        <p>Gramado & Canela • O melhor da Serra Gaúcha</p>
      </header>

      {step === 'catalog' ? (
        <>
      <nav style={styles.nav}>
        {['TRANSFERS', 'INGRESSOS', 'PACOTES', 'EXPERIENCIAS'].map(cat => (
          <button 
            key={cat} 
            onClick={() => setCategory(cat)}
            style={category === cat ? styles.navBtnActive : styles.navBtn}
          >
            {cat}
          </button>
        ))}
      </nav>

      <div style={styles.grid}>
        {services.filter(s => (s.categoria || s.tipo) === category).map(service => (
          <div key={service.id} style={styles.card}>
            {service.imagem_url ? (
              <img src={service.imagem_url} alt={service.nome} style={styles.image} />
            ) : (
              <div style={styles.imagePlaceholder}>📸</div>
            )}
            <h3>{service.nome}</h3>
            <p>{service.descricao}</p>
            <div style={styles.priceRow}>
              <span>A partir de <strong>R$ {parseFloat(service.valor || 0).toLocaleString('pt-BR', {minimumFractionDigits: 2})}</strong></span>
              <button onClick={() => addToCart(service)} style={styles.addBtn}>Selecionar</button>
            </div>
          </div>
        ))}
      </div>
        </>
      ) : (
        <div style={styles.formCard}>
          <h2>Quase lá! Complete os dados</h2>
          <div style={styles.inputGroup}>
            <label>Local de Embarque (Origem)</label>
            <input type="text" placeholder="Ex: Aeroporto Salgado Filho" onChange={e => setBookingData({...bookingData, origem: e.target.value})} style={styles.input}/>
            
            <label>Local de Desembarque (Destino)</label>
            <input type="text" placeholder="Ex: Hotel em Gramado" onChange={e => setBookingData({...bookingData, destino: e.target.value})} style={styles.input}/>
            
            <div style={{display: 'flex', gap: '10px'}}>
              <div style={{flex: 1}}>
                <label>Data</label>
                <input type="date" onChange={e => setBookingData({...bookingData, data: e.target.value})} style={styles.input}/>
              </div>
              <div style={{flex: 1}}>
                <label>Hora</label>
                <input type="time" onChange={e => setBookingData({...bookingData, hora: e.target.value})} style={styles.input}/>
              </div>
            </div>
          </div>
          <button onClick={handleCheckout} style={styles.finishBtnFull}>Finalizar via WhatsApp</button>
          <button onClick={() => setStep('catalog')} style={styles.backBtn}>Voltar ao catálogo</button>
        </div>
      )}

    </div>
  );
}

const styles = {
  container: { fontFamily: 'sans-serif', padding: '20px', maxWidth: '800px', margin: '0 auto', background: '#f8fafc' },
  header: { textAlign: 'center', marginBottom: '30px' },
  nav: { display: 'flex', gap: '10px', marginBottom: '20px', justifyContent: 'center' },
  navBtn: { padding: '10px 20px', borderRadius: '20px', border: '1px solid #ddd', cursor: 'pointer', background: '#fff' },
  navBtnActive: { padding: '10px 20px', borderRadius: '20px', border: 'none', background: '#4c1d95', color: '#fff', cursor: 'pointer' },
  grid: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' },
  card: { background: '#fff', padding: '15px', borderRadius: '15px', boxShadow: '0 4px 6px rgba(0,0,0,0.05)' },
  image: { width: '100%', height: '150px', objectFit: 'cover', borderRadius: '10px', marginBottom: '10px' },
  imagePlaceholder: { width: '100%', height: '150px', background: '#e2e8f0', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '10px' },
  priceRow: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '15px' },
  addBtn: { background: '#10b981', color: '#fff', border: 'none', padding: '8px 15px', borderRadius: '8px', cursor: 'pointer' },
  formCard: { background: '#fff', padding: '25px', borderRadius: '20px', boxShadow: '0 10px 25px rgba(0,0,0,0.05)' },
  inputGroup: { display: 'flex', flexDirection: 'column', gap: '10px', margin: '20px 0' },
  input: { padding: '12px', borderRadius: '10px', border: '1px solid #ddd', fontSize: '16px' },
  finishBtnFull: { width: '100%', background: '#25D366', color: '#fff', border: 'none', padding: '15px', borderRadius: '12px', fontWeight: 'bold', fontSize: '18px', cursor: 'pointer' },
  backBtn: { width: '100%', background: 'transparent', color: '#64748b', border: 'none', marginTop: '10px', cursor: 'pointer' }
};