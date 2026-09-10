(() => {
  if (!("serviceWorker" in navigator)) return;
  let deferredPrompt = null;
  const installButton = document.querySelector("[data-pwa-install]");
  const updateBanner = document.querySelector("[data-pwa-update]");
  const updateButton = document.querySelector("[data-pwa-update-action]");
  const iosHint=document.querySelector("[data-ios-install-hint]");
  const isIOS=/iphone|ipad|ipod/i.test(navigator.userAgent) || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
  const standalone=window.matchMedia("(display-mode: standalone)").matches || window.navigator.standalone === true;
  if(isIOS && !standalone && !sessionStorage.getItem("jf-ios-install-dismissed")){ if(iosHint) iosHint.hidden=false; }
  document.querySelector("[data-ios-install-close]")?.addEventListener("click",()=>{ if(iosHint) iosHint.hidden=true; sessionStorage.setItem("jf-ios-install-dismissed","1"); });

  window.addEventListener("beforeinstallprompt", event => {
    event.preventDefault(); deferredPrompt = event;
    if (installButton) installButton.hidden = false;
  });
  installButton?.addEventListener("click", async () => {
    if (!deferredPrompt) return; deferredPrompt.prompt(); await deferredPrompt.userChoice;
    deferredPrompt = null; installButton.hidden = true;
  });
  window.addEventListener("appinstalled", () => { if (installButton) installButton.hidden = true; });

  navigator.serviceWorker.register("/service-worker.js", { updateViaCache: "none" }).then(registration => {
    function showUpdate(worker) {
      if (!navigator.serviceWorker.controller || !worker) return;
      if (updateBanner) updateBanner.hidden = false;
      updateButton?.addEventListener("click", () => worker.postMessage({type:"SKIP_WAITING"}), {once:true});
    }
    if (registration.waiting) showUpdate(registration.waiting);
    registration.addEventListener("updatefound", () => {
      const worker = registration.installing;
      worker?.addEventListener("statechange", () => { if (worker.state === "installed") showUpdate(worker); });
    });
  }).catch(error => console.debug("Service Worker konnte nicht registriert werden", error));
  navigator.serviceWorker.addEventListener("controllerchange", () => location.reload());
})();


window.JFPush = {
  async subscribe(publicKey) {
    if (!("serviceWorker" in navigator) || !("PushManager" in window)) throw new Error("Push wird von diesem Browser nicht unterstützt.");
    const permission = await Notification.requestPermission();
    if (permission !== "granted") throw new Error("Benachrichtigungen wurden nicht erlaubt.");
    const registration = await navigator.serviceWorker.ready;
    const base64 = publicKey.replace(/-/g,"+").replace(/_/g,"/");
    const raw = atob(base64 + "=".repeat((4-base64.length%4)%4));
    const key = Uint8Array.from([...raw].map(c=>c.charCodeAt(0)));
    const subscription = await registration.pushManager.subscribe({userVisibleOnly:true,applicationServerKey:key});
    const csrf=document.querySelector('[name=csrfmiddlewaretoken]')?.value||document.cookie.match(/csrftoken=([^;]+)/)?.[1]||"";
    const response=await fetch("/benachrichtigungen/push/subscribe/",{method:"POST",headers:{"Content-Type":"application/json","X-CSRFToken":csrf},body:JSON.stringify(subscription)});
    if(!response.ok) throw new Error("Gerät konnte nicht registriert werden.");
    return subscription;
  }
};
