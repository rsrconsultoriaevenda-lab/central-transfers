import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8001';

export default function Storefront() {
  const [services, setServices] = useState([]);
  const [cart, setCart] = useState([]);
  const [category, setCategory] = useState('TRANSFERS'); 

  useEffect(() => {
    // Busca serviços cadastrados no seu backend
    axios.get(`${API_URL}/servicos`).then(res => setServices(res.data));
  }, []);

  const addToCart = (service) => {
    setCart([...cart, service]);
  };

  const handleCheckout = () => {
    // Aqui você enviaria para o seu backend para criar o pedido 
    // e depois redirecionaria para o WhatsApp da Central
    const message = `Olá! Gostaria de reservar: ${cart.map(i => i.nome).join(', ')}`;
    window.location.href = `https://wa.me/SEU_NUMERO?text=${encodeURIComponent(message)}`;
  };

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <h1>Central Transfers & Experiences</h1>
        <p>Gramado & Canela • O melhor da Serra Gaúcha</p>
      </header>

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

      {cart.length > 0 && (
        <div style={styles.checkoutBar}>
          <span>{cart.length} itens selecionados</span>
          <button onClick={handleCheckout} style={styles.finishBtn}>Reservar via WhatsApp</button>
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
  checkoutBar: { position: 'fixed', bottom: '20px', left: '50%', transform: 'translateX(-50%)', background: '#4c1d95', color: '#fff', padding: '15px 30px', borderRadius: '40px', display: 'flex', gap: '20px', alignItems: 'center', boxShadow: '0 10px 25px rgba(0,0,0,0.3)' },
  finishBtn: { background: '#fff', color: '#4c1d95', border: 'none', padding: '10px 20px', borderRadius: '20px', fontWeight: 'bold', cursor: 'pointer' }
};