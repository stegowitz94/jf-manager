{% load static %}
const CACHE_NAME = "jf-manager-shell-v100";
const OFFLINE_URL = "/offline/";
const SHELL = [
  OFFLINE_URL,
  "{% static 'css/app.css' %}",
  "{% static 'js/pwa.js' %}",
  "{% static 'icons/icon-192.png' %}",
  "{% static 'icons/icon-512.png' %}"
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(SHELL))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("message", event => {
  if (event.data?.type === "SKIP_WAITING") self.skipWaiting();
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", event => {
  const request = event.request;
  if (request.method !== "GET") return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  if (request.mode === "navigate") {
    event.respondWith(fetch(request).catch(() => caches.match(OFFLINE_URL)));
    return;
  }

  if (url.pathname.startsWith("/static/css/") || url.pathname.startsWith("/static/js/")) {
    event.respondWith(
      fetch(request)
        .then(response => {
          if (response.ok) {
            const copy = response.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(request, copy));
          }
          return response;
        })
        .catch(() => caches.match(request))
    );
    return;
  }

  if (url.pathname.startsWith("/static/icons/")) {
    event.respondWith(
      caches.match(request).then(cached => cached || fetch(request).then(response => {
        if (response.ok) {
          const copy = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(request, copy));
        }
        return response;
      }))
    );
  }
});

self.addEventListener("push", event => {
  let data={title:"JF-Manager",body:"Neue Benachrichtigung",url:"/"};
  try { data={...data,...event.data.json()}; } catch(e) {}
  event.waitUntil(self.registration.showNotification(data.title,{body:data.body,icon:"/static/icons/icon-192.png",badge:"/static/icons/icon-192.png",data:{url:data.url},tag:data.tag||undefined}));
});
self.addEventListener("notificationclick", event => {
  event.notification.close();
  const url=event.notification.data?.url||"/";
  event.waitUntil(clients.matchAll({type:"window",includeUncontrolled:true}).then(list=>{for(const client of list){if("focus" in client){client.navigate(url);return client.focus();}}return clients.openWindow(url);}));
});
