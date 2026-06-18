// Service worker minimale: cache dei soli asset statici (shell).
// Le pagine dinamiche usano sempre la rete (network-first) per non mostrare dati vecchi.
const CACHE = "bc-static-v1";
const ASSETS = [
  "/static/css/style.css",
  "/static/js/app.js",
  "/static/img/logo.png",
  "/static/icons/icon-512.png",
  "/static/manifest.webmanifest",
];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(ASSETS)));
  self.skipWaiting();
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  if (e.request.method !== "GET") return;
  // Solo asset statici dalla cache; tutto il resto va in rete.
  if (url.pathname.startsWith("/static/")) {
    e.respondWith(
      caches.match(e.request).then((hit) => hit || fetch(e.request))
    );
  }
});
