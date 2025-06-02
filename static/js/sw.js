const CACHE_NAME = "todo-app-v1";
const urlsToCache = [
  "/",
  "/static/css/style.css",
  "/static/js/script.js",
  "/static/img/profile.png",
  "/static/img/wallpaper-threadscity.jpg",
  "https://unpkg.com/boxicons@2.1.4/css/boxicons.min.css",
  "https://unpkg.com/sweetalert/dist/sweetalert.min.js",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(urlsToCache))
  );
});

self.addEventListener("fetch", (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      if (response) {
        return response;
      }
      return fetch(event.request).then((response) => {
        if (!response || response.status !== 200 || response.type !== "basic") {
          return response;
        }
        const responseToCache = response.clone();
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, responseToCache);
        });
        return response;
      });
    })
  );
});
