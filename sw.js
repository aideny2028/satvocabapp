// Service worker: precache the app shell so it works offline and loads
// instantly (the data files alone are ~1.6MB). Bump CACHE_VERSION on deploys
// that change any cached file.
const CACHE_VERSION = 'satvocab-v2';
const CORE = [
  './',
  './index.html',
  './style.css',
  './app.js',
  './ai.js',
  './words.js',
  './sentences.js',
  './templates.js',
  './contextq.js',
  './manifest.json',
  './icon.svg',
  './icon-192.png',
  './icon-512.png'
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE_VERSION).then(c => c.addAll(CORE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE_VERSION).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

// Same-origin GET: stale-while-revalidate — serve cache instantly, refresh in
// the background so the next load picks up deploys. Cross-origin (AI APIs)
// passes straight through to the network.
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET' || url.origin !== location.origin) return;
  e.respondWith(
    caches.open(CACHE_VERSION).then(cache =>
      cache.match(e.request).then(cached => {
        const refresh = fetch(e.request).then(res => {
          if (res && res.ok) cache.put(e.request, res.clone());
          return res;
        }).catch(() => cached);
        return cached || refresh;
      })
    )
  );
});
