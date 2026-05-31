self.addEventListener('install', () => {
  self.skipWaiting();
});

self.addEventListener('push', (event) => {
  let data = {
    title: 'CENTRAL TRANSFER',
    body: 'Você tem uma nova atualização.',
    vibrate: [200, 100, 200],
    url: '/dashboard'
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
    icon: '/pwa-192x192.png', // Certifique-se de que este ícone existe em public/
    badge: '/pwa-192x192.png',
    vibrate: data.vibrate,
    data: {
      url: data.url
    },
    tag: 'central-notification',
    renotify: true
  };

  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const urlToOpen = new URL(event.notification.data.url, self.location.origin).href;

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then((windowClients) => {
      for (let client of windowClients) {
        if (client.url === urlToOpen && 'focus' in client) return client.focus();
      }
      if (clients.openWindow) return clients.openWindow(urlToOpen);
    })
  );
});