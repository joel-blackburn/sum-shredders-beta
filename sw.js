/* Sum Shredders offline support (Captain Dad Games).
   - On first visit, saves the game, 3D engine, fonts, icons and Dad's voice clips on the device.
   - The game page and voice list are "network first": when online you always get the newest version;
     when offline the saved copy is used.
   - Everything else is served from the saved copy and refreshed in the background.
   Bump VERSION only if the caching rules themselves change; normal game updates arrive automatically. */
const VERSION = 'v1';
const CACHE = 'sum-shredders-' + VERSION;
const CORE = [
  './',
  'index.html',
  'lib/three.min.js',
  'fonts/fonts.css',
  'fonts/bungee-400.woff2',
  'fonts/nunito-400.woff2',
  'fonts/nunito-600.woff2',
  'fonts/nunito-700.woff2',
  'fonts/nunito-800.woff2',
  'fonts/nunito-900.woff2',
  'brand/captain-dad-32.png',
  'voice/index.json'
];
const FRESH = [/\/$/, /\/index\.html$/, /\/voice\/index\.json$/];

self.addEventListener('install', event => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE);
    await cache.addAll(CORE);
    // Icons and manifest for whichever channel this is (beta or prod) are listed in the page;
    // Dad's clips are listed in voice/index.json. Missing extras never block install.
    const extras = ['brand/favicon-32.png', 'brand/apple-touch-icon.png', 'brand/site.webmanifest',
      'brand/beta/favicon-32.png', 'brand/beta/apple-touch-icon.png', 'brand/beta/site.webmanifest'];
    try {
      const j = await (await fetch('voice/index.json', { cache: 'no-cache' })).json();
      (j.clips || []).forEach(id => extras.push(`voice/${id}.mp3`));
    } catch (e) {}
    await Promise.all(extras.map(u => cache.add(u).catch(() => {})));
    self.skipWaiting();
  })());
});

self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    for (const k of await caches.keys()) if (k.startsWith('sum-shredders-') && k !== CACHE) await caches.delete(k);
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', event => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;          // never touch other sites
  if (url.pathname.startsWith('/_vercel/')) return;     // analytics: online only
  if (url.pathname.endsWith('/studio.html')) return;    // recording page: online only

  const fresh = req.mode === 'navigate' || FRESH.some(r => r.test(url.pathname));
  event.respondWith(fresh ? networkFirst(req) : staleWhileRevalidate(event, req));
});

async function networkFirst(req) {
  const cache = await caches.open(CACHE);
  try {
    const res = await fetch(req, { cache: 'no-cache' });
    if (res.ok) cache.put(req.mode === 'navigate' ? 'index.html' : req, res.clone());
    return res;
  } catch (e) {
    return (await cache.match(req, { ignoreSearch: true })) ||
           (req.mode === 'navigate' ? await cache.match('index.html') : undefined) ||
           Response.error();
  }
}

async function staleWhileRevalidate(event, req) {
  const cache = await caches.open(CACHE);
  // Voice clips are requested as clip.mp3?v=<version>; fall back to any saved copy when offline.
  const hit = (await cache.match(req)) || (await cache.match(req, { ignoreSearch: true }));
  const update = fetch(req).then(res => { if (res.ok) cache.put(req, res.clone()); return res; });
  if (hit) { event.waitUntil(update.catch(() => {})); return hit; }
  return update.catch(() => Response.error());
}
