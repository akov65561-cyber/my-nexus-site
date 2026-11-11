self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open('nexus-store').then((cache) => cache.addAll([
      'index.html',
      'game.html'
    ]))
  );
});

self.addEventListener('fetch', (e) => {
  e.respondWith(
    caches.match(e.request).then((response) => response || fetch(e.request))
  );
});