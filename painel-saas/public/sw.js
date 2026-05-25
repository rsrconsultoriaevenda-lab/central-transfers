/* eslint-disable no-restricted-globals */

// Evento de Push: Recebe a mensagem do Backend (pywebpush)
self.addEventListener('push', (event) => {
  if (!(self.Notification && self.Notification.permission === 'granted')) {
    return;
  }

  let data = {
    title: 'Nova Solicitação',
    body: 'Você tem um novo transfer disponível!',
    vibrate: [200, 100, 200],
    data: { url: '/dashboard/pedidos' }
  };

  if (event.data) {
    try {
      data = event.data.json();
    } catch (e) {
      data.body = event.data.text();
    }
  }

  const options = {
    body: data.body,
    icon: '/icon-192x192.png',
    badge: '/badge-72x72.png',
    vibrate: data.vibrate || [500, 110, 500],
    data: data.data || { url: '/' },
    actions: [
      { action: 'open', title: 'Ver Detalhes' },
      { action: 'close', title: 'Ignorar' }
    ],
    tag: 'transfer-notification',
    renotify: true
  };

  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

// Evento de Clique: Direciona o motorista para o pedido
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  if (event.action === 'close') return;

  const urlToOpen = event.notification.data.url || '/';

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then((windowClients) => {
      if (windowClients.length > 0) return windowClients[0].focus();
      return clients.openWindow(urlToOpen);
    })
  );
});