/* Service worker do Obra Facil — Casa Caio
   Objetivo: abrir o app mesmo sem internet.

   Regras:
   - HTML do app: rede primeiro (sempre pega a versao nova), cache como reserva.
   - Bibliotecas de CDN e icones: cache primeiro.
   - Supabase: nunca passa pelo cache.
*/

const CACHE = 'obra-facil-v1';

const ESSENCIAIS = [
  '/',
  '/index.html',
  '/manifest.webmanifest',
  '/icon-192.png',
  '/icon-512.png',
  '/apple-touch-icon.png',
  'https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js',
  'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/dist/umd/supabase.js',
  'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
];

self.addEventListener('install', (evento) => {
  evento.waitUntil(
    caches.open(CACHE)
      .then((cache) => Promise.all(
        ESSENCIAIS.map((url) => cache.add(new Request(url, { cache: 'reload' })).catch(() => null))
      ))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (evento) => {
  evento.waitUntil(
    caches.keys()
      .then((chaves) => Promise.all(chaves.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (evento) => {
  const req = evento.request;
  if (req.method !== 'GET') return;

  let url;
  try { url = new URL(req.url); } catch (e) { return; }

  // Nada de cache para o banco de dados
  if (url.hostname.endsWith('supabase.co')) return;

  const ehPagina = req.mode === 'navigate' || url.pathname === '/' || url.pathname.endsWith('/index.html');

  if (ehPagina) {
    // Rede primeiro: se online, o usuario sempre recebe a versao publicada
    evento.respondWith(
      fetch(req)
        .then((resp) => {
          if (resp && resp.ok) {
            const copia = resp.clone();
            caches.open(CACHE).then((c) => c.put('/index.html', copia)).catch(() => {});
          }
          return resp;
        })
        .catch(() => caches.match('/index.html').then((hit) => hit || caches.match('/')))
    );
    return;
  }

  // Demais arquivos: cache primeiro
  evento.respondWith(
    caches.match(req).then((hit) => {
      if (hit) return hit;
      return fetch(req)
        .then((resp) => {
          const guardavel = resp && (resp.ok || resp.type === 'opaque');
          if (guardavel) {
            const copia = resp.clone();
            caches.open(CACHE).then((c) => c.put(req, copia)).catch(() => {});
          }
          return resp;
        })
        .catch(() => hit);
    })
  );
});
