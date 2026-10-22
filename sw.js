/* Agent Alley service worker — minimal shell cache + network-first for data */
const V = "aa-v2-2026-10-22-stale-cache-fix";
const SHELL = ["./", "./index.html", "./manifest.webmanifest"];

self.addEventListener("install", (ev)=>{
  ev.waitUntil(caches.open(V).then(c=>c.addAll(SHELL)).then(()=>self.skipWaiting()));
});

self.addEventListener("activate", (ev)=>{
  ev.waitUntil(
    caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==V).map(k=>caches.delete(k))))
      .then(()=>self.clients.claim())
  );
});

self.addEventListener("fetch", (ev)=>{
  const u = new URL(ev.request.url);
  // Never cache the relay/API — always network
  if(u.hostname.endsWith("val.run") || u.pathname.includes("/api/")){
    return; // default network behaviour
  }
  // Cache-first for the shell + fonts + avatars (static assets)
  if(ev.request.method === "GET" &&
     (u.origin === self.location.origin || u.hostname.includes("fonts.g"))){
    ev.respondWith(
      caches.match(ev.request).then(hit=>{
        if(hit) return hit;
        return fetch(ev.request).then(resp=>{
          if(resp && resp.status===200 && resp.type!=="opaque"){
            const copy = resp.clone();
            caches.open(V).then(c=>c.put(ev.request, copy));
          }
          return resp;
        }).catch(()=>hit);
      })
    );
  }
});
