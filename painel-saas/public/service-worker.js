self.addEventListener('install', (event) => {
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    event.waitUntil(self.clients.claim());
});

// 1. Listener para Push Notifications REAIS (Vindo do Servidor via VAPID/Push Service)
self.addEventListener('push', (event) => {
    const data = event.data ? event.data.json() : {};
    
    const title = data.title || "🚖 Novo Pedido Disponível";
    const options = {
        body: data.mensagem || `Nova corrida de R$ ${data.valor}`,
        icon: '/icon-192x192.png',
        badge: '/badge-72x72.png',
        vibrate: [200, 100, 200, 100, 200],
        tag: 'new-order-alert',
        renotify: true,
        data: {
            url: data.pedido_id ? `/pedidos/${data.pedido_id}` : '/'
        }
    };

    event.waitUntil(self.registration.showNotification(title, options));
});

// 2. Listener para mensagens internas do App (Ex: WebSocket comunicando com o SW)
self.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'SHOW_NOTIFICATION') {
        const { payload } = event.data;
        self.registration.showNotification('🚖 Novo Pedido Recebido', {
            body: `${payload.origem} -> ${payload.destino}\nValor: R$ ${payload.valor}`,
            icon: '/icon-192x192.png',
            tag: 'new-order-ws'
        });
    }
});

// 3. Clique na Notificação: Abre o PWA ou foca na aba já aberta
self.addEventListener('notificationclick', (event) => {
    event.notification.close();
    const urlToOpen = event.notification.data?.url || '/';

    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true }).then((windowClients) => {
            for (let client of windowClients) {
                if (client.url === urlToOpen && 'focus' in client) return client.focus();
            }
            if (clients.openWindow) return clients.openWindow(urlToOpen);
        })
    );
});