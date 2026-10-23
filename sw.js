/* Agent Alley service worker — network-first for HTML (no stale cache ever), cache-first for images/fonts only */
const V = "aa-v7-2026-10-23-ali-launcher";

self.addEventListener("install", (ev)=>{
  // Don't pre-cache the HTML. Just activate immediately.
  self.skipWaiting();
});

self.addEventListener("activate", (ev)=>{
  ev.waitUntil(
    caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==V).map(k=>caches.delete(k))))
      .then(()=>self.clients.claim())
  );
});

self.addEventListener("fetch", (ev)=>{
  const u = new URL(ev.request.url);
  const req = ev.request;

  // Never cache the relay/API — always network
  if(u.hostname.endsWith("val.run") || u.pathname.includes("/api/")){
    return;
  }

  // HTML (index.html, root) → NETWORK FIRST, no cache fallback
  // This guarantees Devon always gets the freshest dashboard, never stale.
  if(req.method === "GET" && (u.pathname === "/" || u.pathname.endsWith("/") || u.pathname.endsWith(".html"))){
    ev.respondWith(
      fetch(req, {cache: "no-store"}).catch(()=>{
        // Only fall back to cache if network is completely dead (offline)
        return caches.match(req);
      })
    );
    return;
  }

  // Static assets (images, fonts, manifest) → cache-first for performance
  if(req.method === "GET" && u.origin === self.location.origin){
    ev.respondWith(
      caches.match(req).then(hit=>{
        if(hit) return hit;
        return fetch(req).then(resp=>{
          if(resp && resp.status===200 && resp.type!=="opaque"){
            const copy = resp.clone();
            caches.open(V).then(c=>c.put(req, copy));
          }
          return resp;
        }).catch(()=>hit);
      })
    );
  }
});

/* Notification click: focus an open Agent Alley tab, or open a fresh one. */
self.addEventListener("notificationclick", (ev)=>{
  ev.notification.close();
  ev.waitUntil((async ()=>{
    const all = await clients.matchAll({type:"window", includeUncontrolled:true});
    for(const c of all){
      if(c.url.includes("/agent-alley/")){
        try { await c.focus(); return; } catch(e){}
      }
    }
    try { await clients.openWindow("/agent-alley/"); } catch(e){}
  })());
});
