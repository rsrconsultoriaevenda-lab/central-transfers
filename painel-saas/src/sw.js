import { precacheAndRoute } from 'workbox-precaching';
import { registerRoute } from 'workbox-routing';
import { NetworkFirst, CacheFirst } from 'workbox-strategies';
import { ExpirationPlugin } from 'workbox-expiration';

// Injeta automaticamente a lista de arquivos gerada pelo build do Vite
precacheAndRoute(self.__WB_MANIFEST);

// 1. Estratégia para API (Pedidos/Agenda) - Network First
// Tenta a rede para ter dados novos; se falhar (offline), usa o cache.
registerRoute(
  ({ url }) => url.pathname.includes('/pedidos') || url.host.includes('railway.app'),
  new NetworkFirst({
    cacheName: 'api-cache',
    plugins: [
      new ExpirationPlugin({
        maxEntries: 50,
        maxAgeSeconds: 24 * 60 * 60, // 24 horas
      }),
    ],
  })
);

// 2. Estratégia para Imagens e Assets Externos - Cache First
registerRoute(
  ({ request }) => request.destination === 'image',
  new CacheFirst({
    cacheName: 'images-cache',
    plugins: [
      new ExpirationPlugin({
        maxEntries: 60,
        maxAgeSeconds: 30 * 24 * 60 * 60, // 30 dias
      }),
    ],
  })
);

// 3. Escuta de Mensagens Push (Notificações do Motorista)
self.addEventListener('push', (event) => {
  try {
    const data = event.data ? event.data.json() : { title: 'Nova Chamada', body: 'Verifique sua agenda!' };
    
    const options = {
      body: data.body,
      icon: '/pwa-192x192.png',
      badge: '/favicon.svg',
      vibrate: [200, 100, 200],
      data: { url: '/dashboard' } // URL para abrir ao clicar
    };

    event.waitUntil(
      self.registration.showNotification(data.title, options)
    );
  } catch (err) {
    console.error('Erro ao processar Push:', err);
  }
});

// 4. Clique na Notificação (Leva o motorista para o App)
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  event.waitUntil(
    clients.matchAll({ type: 'window' }).then((clientList) => {
      if (clientList.length > 0) return clientList[0].focus();
      return clients.openWindow(event.notification.data.url || '/');
    })
  );
});