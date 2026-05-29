import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_URL } from './App';

// Configuração de Branding
const tenantConfig = {
  name: 'LUXE SERRA',
  primaryColor: '#4c1d95',
  secondaryColor: '#7c3aed',
  heroImage: 'https://images.unsplash.com/photo-1449965408869-eaa3f722e40d?auto=format&fit=crop&q=80&w=2000',
  welcomeMessage: 'Sua Jornada de Luxo Começa Aqui'
};

const THEME = {
  primary: tenantConfig.primaryColor,
  secondary: tenantConfig.secondaryColor,
  bg: '#F8FAFC',
  surface: '#FFFFFF',
  text: '#1e293b',
  muted: '#64748b'
};

export default function Storefront() {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState('ALL');
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [isCheckingOut, setIsCheckingOut] = useState(false);
  const [cart, setCart] = useState(() => {
    const saved = localStorage.getItem('cart');
    return saved ? JSON.parse(saved) : [];
  });
  const [bookingDetails, setBookingDetails] = useState({
    nome: '', email: '', telefone: '', cpf: '', origem: '', destino: '', data: '', observacoes: ''
  });
  const [weather] = useState({ temp: 25, condition: 'Ensolarado' });
  const [referralCode, setReferralCode] = useState(localStorage.getItem('referral_code') || null);

  useEffect(() => {
    localStorage.setItem('cart', JSON.stringify(cart));
  }, [cart]);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const ref = params.get('ref');
    if (ref) {
      setReferralCode(ref);
      localStorage.setItem('referral_code', ref);
    }
  }, []);

  useEffect(() => {
    const fetchServices = async () => {
      try {
        const res = await axios.get(`${API_URL}/servicos/`);
        setServices(res.data);
      } catch (err) {
        setServices([
          { id: 1, nome: 'Premium Transfer: Aero POA', categoria: 'TRANSFERS', valor: 350.00, descricao: 'Transporte privativo em Sedan de Luxo.', imagem_url: '' },
          { id: 2, nome: 'Tour Privativo: Vale dos Vinhedos', categoria: 'EXPERIENCIAS', valor: 1200.00, descricao: 'Experiência exclusiva.', imagem_url: '' }
        ]);
      } finally {
        setLoading(false);
      }
    };
    fetchServices();
  }, []);

  const updateQuantity = (index, delta) => {
    setCart(prev => prev.map((item, i) => i === index ? {...item, quantidade: Math.max(1, (item.quantidade || 1) + delta)} : item));
  };

  const removeFromCart = (index) => setCart(prev => prev.filter((_, i) => i !== index));

  const handleCPFChange = (e) => {
    let value = e.target.value.replace(/\D/g, ''); // Remove tudo que não é dígito
    if (value.length > 11) value = value.slice(0, 11);
    
    value = value.replace(/(\d{3})(\d)/, '$1.$2');
    value = value.replace(/(\d{3})(\d)/, '$1.$2');
    value = value.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
    setBookingDetails({ ...bookingDetails, cpf: value });
  };

  // ... dentro do bloco de retorno do Drawer, onde estão os outros inputs ...
  // Inserindo o campo visualmente no formulário
  const renderFormFields = () => (
    <>
      <input 
        style={styles.drawerInput} 
  };

  // ... dentro do bloco de retorno do Drawer, onde estão os outros inputs ...
  // Inserindo o campo visualmente no formulário
  const renderFormFields = () => (
    <>
      <input 
        style={styles.drawerInput} 
        placeholder="Seu Nome Completo" 
        value={bookingDetails.nome}
        onChange={e => setBookingDetails({...bookingDetails, nome: e.target.value})}
      />
      <input 
        style={styles.drawerInput  
        placeholder="Seu E-mail (Obrigatório para Pix)" 
        value={bookingDetails.email}
        onChange={e => setBookingDetails({...bookingDetails, email: e.target.value})}
      />
      <input 
        style={styles.drawerInput} 
        placeholder="Seu WhatsApp/Telefone" 
        value={bookingDetails.telefone}
        onChange={e => setBookingDetails({...bookingDetails, telefone: e.target.value})}
      />
      <input 
        style={styles.drawerInput} 
        placeholder="CPF (Opcional - Melhora aprovação do cartão)" 
        value={bookingDetails.cpf}
        onChange={handleCPFChange}
      />
      <input 
        style={styles.drawerInput} 
        placeholder="Local de Origem" 
        value={bookingDetails.origem}
        onChange={e => setBookingDetails({...bookingDetails, origem: e.target.value})}
      />
      <input 
        style={styles.drawerInput} 
        placeholder="Local de Destino" 
        value={bookingDetails.destino}
        onChange={e => setBookingDetails({...bookingDetails, destino: e.target.value})}
      />
    </>
  )     placeholder="Seu Nome Completo" 
        value={bookingDetails.nome}
        onChange={e => setBookingDetails({...bookingDetails, nome: e.target.value})}
      />
      <input 
        style={styles.drawerInput} 
        placeholder="Seu E-mail (Obrigatório para Pix)" 
        value={bookingDetails.email}
        onChange={e => setBookingDetails({...bookingDetails, email: e.target.value})}
      />
      <input 
        style={styles.drawerInput} 
        placeholder="Seu WhatsApp/Telefone" 
        value={bookingDetails.telefone}
        onChange={e => setBookingDetails({...bookingDetails, telefone: e.target.value})}
      />
      <input 
        style={styles.drawerInput} 
        placeholder="CPF (Opcional - Melhora aprovação do cartão)" 
        value={bookingDetails.cpf}
        onChange={handleCPFChange}
      />
      <input 
        style={styles.drawerInput} 
        placeholder="Local de Origem" 
        value={bookingDetails.origem}
        onChange={e => setBookingDetails({...bookingDetails, origem: e.target.value})}
      />
      <input 
        style={styles.drawerInput} 
        placeholder="Local de Destino" 
        value={bookingDetails.destino}
        onChange={e => setBookingDetails({...bookingDetails, destino: e.target.value})}
      />
    </>
  );

  const handleCheckout = async () => {
    if (!bookingDetails.nome || !bookingDetails.email || !bookingDetails.telefone || !bookingDetails.origem || !bookingDetails.destino) {
      alert("Por favor, preencha todos os campos obrigatórios: Nome, E-mail, Telefone, Origem e Destino.");
      return;
    }
    setIsCheckingOut(true);
    try {
      const res = await axios.post(`${API_URL}/pagamentos/checkout/`, {
        itens: cart,
        metadata: { ...bookingDetails, parceiro_cod: referralCode }
      });
      if (res.data.init_point) window.location.href = res.data.init_point;
    } catch (err) {
      alert("Erro ao processar reserva.");
    } finally {
      setIsCheckingOut(false);
    }
  };

  // ... (Manter o restante da estrutura de renderização e styles que você definiu)
  // Certifique-se de que o return está completo como no seu original.
  return (
      <div style={styles.container}>
        {/* Adicione o JSX do Navbar, Hero, Main e Footer conforme o seu código anterior */}
      </div>
  );
}

// ... (Manter o objeto 'styles' que você definiu no final do seu código)