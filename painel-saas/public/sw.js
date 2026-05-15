const CACHE_NAME = 'central-v2';
const STATIC_ASSETS = ['/', '/index.html', '/driver', '/favicon.ico', '/logo192.png'];
const API_URL_MATCH = /\/pedidos/;

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
  );
});

self.addEventListener('fetch', (event) => {
  const url = event.request.url;

  // Estratégia Network-First para a API de Pedidos (Agenda)
  // Tenta buscar a versão mais recente; se falhar (offline), usa o cache.
  if (API_URL_MATCH.test(url)) {
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          const clonedResponse = response.clone();
          caches.open('api-cache').then((cache) => cache.put(event.request, clonedResponse));
          return response;
        })
        .catch(() => caches.match(event.request))
    );
  } else {
    // Estratégia Cache-First para arquivos estáticos (CSS, JS, Imagens)
    event.respondWith(
      caches.match(event.request).then((response) => response || fetch(event.request))
    );
  }
});

self.addEventListener('push', (event) => {
  const data = event.data.json();
  self.registration.showNotification(data.title, {
    body: data.body,
    icon: '/logo192.png',
    vibrate: data.vibrate || [200, 100, 200]
  });
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  event.waitUntil(
    clients.openWindow('/driver')
  );
});