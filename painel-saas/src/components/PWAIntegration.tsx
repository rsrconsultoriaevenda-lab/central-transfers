import React, { useEffect } from 'react';

const PWAIntegration: React.FC = () => {
  const VAPID_PUBLIC_KEY = import.meta.env.VITE_VAPID_PUBLIC_KEY;
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001/api';

  useEffect(() => {
    const initPWA = async () => {
      if ('serviceWorker' in navigator && 'PushManager' in window) {
        try {
          const registration = await navigator.serviceWorker.register('/sw.js');
          console.log('✅ Service Worker registrado');

          const permission = await Notification.requestPermission();
          if (permission === 'granted') {
            await subscribeUser(registration);
          }
        } catch (error) {
          console.error('❌ Erro ao configurar PWA:', error);
        }
      }
    };

    initPWA();
  }, []);

  const urlBase64ToUint8Array = (base64String: string) => {
    const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
    const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
  };

  const subscribeUser = async (registration: ServiceWorkerRegistration) => {
    try {
      if (!VAPID_PUBLIC_KEY) {
        console.warn('⚠️ VITE_VAPID_PUBLIC_KEY não configurada no .env');
        return;
      }

      let subscription = await registration.pushManager.getSubscription();

      if (!subscription) {
        subscription = await registration.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY),
        });
      }

      const token = localStorage.getItem('token');
      if (!token) return;

      // Envia a subscrição completa para o backend
      const response = await fetch(`${API_URL}/notifications/subscribe`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(subscription),
      });

      if (response.ok) {
        console.log('🚀 Subscrição de Push sincronizada com o servidor');
      }
    } catch (error) {
      console.error('❌ Erro ao subscrever para Push Notifications:', error);
    }
  };

  return null;
};

export default PWAIntegration;