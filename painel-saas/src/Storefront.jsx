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

  // Dicas dinâmicas para atrair o cliente
  const gramadoTips = [
    { id: 1, icon: '🌲', title: 'Lago Negro', desc: 'Perfeito para um passeio de pedalinho ao entardecer.' },
    { id: 2, icon: '🍫', title: 'Rua Coberta', desc: 'O melhor lugar para um chocolate quente artesanal.' },
    { id: 3, icon: '❄️', title: 'Snowland', desc: 'Diversão na neve o ano todo em Gramado.' },
    { id: 4, icon: '🍷', title: 'Vale dos Vinhedos', desc: 'Uma experiência gastronômica inesquecível.' }
  ];

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
      {/* Hero Section Cromático */}
      <div style={styles.hero}>
        <div style={styles.heroOverlay}>
          <h1 style={styles.heroTitle}>Viva a Magia da Serra</h1>
          <p style={styles.heroSubtitle}>Transfers exclusivos e experiências inesquecíveis em Gramado e Canela</p>
        </div>
      </div>

      {step === 'catalog' ? (
        <>
      {/* Dicas de Gramado (Diferencial) */}
      <section style={styles.tipsSection}>
        <h2 style={styles.sectionTitle}>Dicas da Serra 🏔️</h2>
        <div style={styles.tipsGrid}>
          {gramadoTips.map(tip => (
            <div key={tip.id} style={styles.tipCard}>
              <span style={styles.tipIcon}>{tip.icon}</span>
              <h4 style={styles.tipTitle}>{tip.title}</h4>
              <p style={styles.tipDesc}>{tip.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <h2 style={styles.sectionTitle}>Nossos Serviços</h2>
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
          <h2 style={styles.formTitle}>Quase lá! 🚖</h2>
          <p style={styles.formSubtitle}>Confirme os detalhes para sua reserva premium</p>
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
  container: { fontFamily: '"Inter", sans-serif', padding: '0 0 40px 0', maxWidth: '900px', margin: '0 auto', background: '#f5f3ff', minHeight: '100vh' },
  hero: { 
    height: '350px', 
    backgroundImage: 'url("https://images.unsplash.com/photo-1626014903708-3607062400f0?q=80&w=1200")', 
    backgroundSize: 'cover', 
    backgroundPosition: 'center',
    borderRadius: '0 0 50px 50px',
    position: 'relative',
    overflow: 'hidden',
    marginBottom: '30px'
  },
  heroOverlay: {
    position: 'absolute', top: 0, left: 0, right: 0, bottom: 0,
    background: 'linear-gradient(to bottom, rgba(76, 29, 149, 0.4), rgba(76, 29, 149, 0.9))',
    display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', padding: '20px', textAlign: 'center'
  },
  heroTitle: { color: '#fff', fontSize: '36px', fontWeight: '800', margin: 0, textShadow: '0 2px 10px rgba(0,0,0,0.3)' },
  heroSubtitle: { color: 'rgba(255,255,255,0.9)', fontSize: '18px', marginTop: '10px', maxWidth: '600px' },
  
  sectionTitle: { fontSize: '22px', color: '#1e1b4b', fontWeight: '700', margin: '30px 20px 20px 20px' },
  
  tipsSection: { padding: '0 20px' },
  tipsGrid: { display: 'flex', gap: '15px', overflowX: 'auto', paddingBottom: '10px', scrollbarWidth: 'none' },
  tipCard: { minWidth: '180px', background: '#fff', padding: '20px', borderRadius: '25px', boxShadow: '0 10px 15px rgba(76, 29, 149, 0.05)', border: '1px solid #ede9fe' },
  tipIcon: { fontSize: '30px', display: 'block', marginBottom: '10px' },
  tipTitle: { fontSize: '14px', fontWeight: '700', color: '#4c1d95', margin: '0 0 5px 0' },
  tipDesc: { fontSize: '12px', color: '#64748b', margin: 0, lineHeight: '1.4' },

  nav: { display: 'flex', gap: '10px', marginBottom: '25px', padding: '0 20px', overflowX: 'auto', scrollbarWidth: 'none' },
  navBtn: { padding: '12px 24px', borderRadius: '25px', border: '1px solid #ddd', cursor: 'pointer', background: '#fff', color: '#64748b', fontWeight: '600', whiteSpace: 'nowrap', transition: '0.3s' },
  navBtnActive: { padding: '12px 24px', borderRadius: '25px', border: 'none', background: '#7c3aed', color: '#fff', cursor: 'pointer', fontWeight: '700', boxShadow: '0 10px 20px rgba(124, 58, 237, 0.3)', whiteSpace: 'nowrap' },
  
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '25px', padding: '0 20px' },
  card: { background: '#fff', padding: '0', borderRadius: '30px', overflow: 'hidden', boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)', transition: 'transform 0.3s' },
  image: { width: '100%', height: '200px', objectFit: 'cover' },
  imagePlaceholder: { width: '100%', height: '200px', background: '#e2e8f0', display: 'flex', alignItems: 'center', justifyContent: 'center' },
  priceRow: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '10px', padding: '0 20px 20px 20px' },
  addBtn: { background: '#7c3aed', color: '#fff', border: 'none', padding: '10px 20px', borderRadius: '15px', fontWeight: '700', cursor: 'pointer' },
  
  formCard: { background: '#fff', padding: '40px', borderRadius: '40px', margin: '0 20px', boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)' },
  formTitle: { fontSize: '28px', color: '#1e1b4b', textAlign: 'center', margin: 0 },
  formSubtitle: { textAlign: 'center', color: '#64748b', marginBottom: '30px' },
  label: { fontSize: '12px', fontWeight: '800', color: '#4c1d95', marginLeft: '5px', textTransform: 'uppercase' },
  inputGroup: { display: 'flex', flexDirection: 'column', gap: '15px', margin: '20px 0' },
  input: { padding: '15px', borderRadius: '18px', border: '2px solid #f1f5f9', fontSize: '16px', outline: 'none', transition: '0.3s' },
  finishBtnFull: { width: '100%', background: '#22c55e', color: '#fff', border: 'none', padding: '18px', borderRadius: '20px', fontWeight: '800', fontSize: '18px', cursor: 'pointer', boxShadow: '0 15px 30px rgba(34, 197, 94, 0.4)' },
  backBtn: { width: '100%', background: 'transparent', color: '#94a3b8', border: 'none', marginTop: '15px', cursor: 'pointer', fontWeight: '600' }
};