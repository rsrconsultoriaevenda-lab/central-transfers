import React, { useState, useEffect } from 'react';

/**
 * Componente para convidar o motorista a instalar o PWA.
 * Funciona capturando o evento 'beforeinstallprompt'.
 */
const InstallPWA: React.FC = () => {
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const handler = (e: Event) => {
      // Impede o Chrome de mostrar o banner automático imediatamente
      e.preventDefault();
      // Guarda o evento para ser disparado pelo nosso botão
      setDeferredPrompt(e);
      // Mostra o nosso componente de convite
      setIsVisible(true);
    };

    window.addEventListener('beforeinstallprompt', handler);

    // Verifica se já está instalado
    if (window.matchMedia('(display-mode: standalone)').matches) {
      setIsVisible(false);
    }

    return () => window.removeEventListener('beforeinstallprompt', handler);
  }, []);

  const handleInstallClick = async () => {
    if (!deferredPrompt) return;

    // Mostra o prompt de instalação nativo
    deferredPrompt.prompt();

    // Aguarda a resposta do usuário
    const { outcome } = await deferredPrompt.userChoice;
    
    if (outcome === 'accepted') {
      console.log('✅ Motorista aceitou a instalação');
    } else {
      console.log('❌ Motorista recusou a instalação');
    }

    // Limpa o prompt e esconde o banner
    setDeferredPrompt(null);
    setIsVisible(false);
  };

  if (!isVisible) return null;

  return (
    <div style={{
      position: 'fixed',
      bottom: '20px',
      left: '20px',
      right: '20px',
      backgroundColor: '#4c1d95', // Roxo do seu tema
      color: 'white',
      padding: '16px',
      borderRadius: '12px',
      display: 'flex',
      flexDirection: 'column',
      gap: '12px',
      boxShadow: '0 4px 20px rgba(0,0,0,0.3)',
      zIndex: 9999,
      border: '1px solid rgba(255,255,255,0.1)'
    }}>
      <div style={{ fontWeight: '600', fontSize: '1rem' }}>
        📲 Instalar App Central Transfers
      </div>
      <div style={{ fontSize: '0.875rem', opacity: 0.9 }}>
        Acesse o painel mais rápido e receba alertas de corridas direto na tela do seu celular.
      </div>
      <button 
        onClick={handleInstallClick}
        style={{
          backgroundColor: 'white',
          color: '#4c1d95',
          border: 'none',
          padding: '10px',
          borderRadius: '8px',
          fontWeight: 'bold',
          cursor: 'pointer',
          transition: 'transform 0.2s'
        }}
        onMouseDown={(e) => e.currentTarget.style.transform = 'scale(0.95)'}
        onMouseUp={(e) => e.currentTarget.style.transform = 'scale(1)'}
      >
        INSTALAR AGORA
      </button>
    </div>
  );
};

export default InstallPWA;