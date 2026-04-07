/**
 * Hercules PWA Service Worker
 * Strategy: cache-first for static assets, network-first for API/HTML.
 */

const CACHE_NAME = 'hercules-v1';

// App shell resources to pre-cache on install
const PRECACHE_URLS = [
  '/',
  '/dashboard',
  '/tracker',
  '/programs',
  '/nutrition',
  '/static/css/style.css',
  '/static/js/main.js',
  '/static/js/animated_bg.js',
  '/static/manifest.json',
  '/static/offline.html',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png',
];

// ── Install ───────────────────────────────────────────────────────────────────
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(PRECACHE_URLS))
  );
  self.skipWaiting();
});

// ── Activate ──────────────────────────────────────────────────────────────────
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((key) => key !== CACHE_NAME)
          .map((key) => caches.delete(key))
      )
    )
  );
  self.clients.claim();
});

// ── Fetch ─────────────────────────────────────────────────────────────────────
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET and cross-origin requests
  if (request.method !== 'GET' || url.origin !== self.location.origin) return;

  // API calls → network-first; fall back to a simple JSON error so the UI
  // can display an offline message instead of a hard browser error.
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request).catch(() =>
        new Response(
          JSON.stringify({ error: 'You appear to be offline.' }),
          { status: 503, headers: { 'Content-Type': 'application/json' } }
        )
      )
    );
    return;
  }

  // Static assets (CSS, JS, images) → cache-first
  if (
    url.pathname.startsWith('/static/') ||
    url.pathname.endsWith('.css') ||
    url.pathname.endsWith('.js') ||
    url.pathname.endsWith('.png') ||
    url.pathname.endsWith('.webp')
  ) {
    event.respondWith(
      caches.match(request).then((cached) => {
        if (cached) return cached;
        return fetch(request).then((response) => {
          if (response && response.status === 200) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
          }
          return response;
        });
      })
    );
    return;
  }

  // HTML pages → network-first, fall back to cached version
  event.respondWith(
    fetch(request)
      .then((response) => {
        if (response && response.status === 200) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
        }
        return response;
      })
      .catch(() => caches.match(request).then((cached) => cached || caches.match('/static/offline.html')))
  );
});
