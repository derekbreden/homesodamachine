// The installed web app manages its push subscription from the inbox.
import { HSM_EVENTS } from "/contracts/client-events.js";

const button = document.getElementById("notifs-push");
const status = document.getElementById("notifs-push-status");
const dialog = document.getElementById("notifs-push-dialog");
let config, token, subscribed = false;

async function messagingToken() {
  const [{ initializeApp }, { getMessaging, getToken, isSupported }] = await Promise.all([
    import("https://www.gstatic.com/firebasejs/10.14.1/firebase-app.js"),
    import("https://www.gstatic.com/firebasejs/10.14.1/firebase-messaging.js"),
  ]);
  if (!(await isSupported())) throw new Error("Push is unavailable in this browser");
  const { vapidKey, ...firebase } = config;
  const registration = await navigator.serviceWorker.register("/firebase-messaging-sw.js", { scope: "/" });
  await navigator.serviceWorker.ready;
  const next = await getToken(getMessaging(initializeApp(firebase)), {
    vapidKey, serviceWorkerRegistration: registration,
  });
  if (!next) throw new Error("Push token unavailable");
  return next;
}

async function setSubscription(enabled) {
  const response = await fetch(enabled ? "/api/push/subscribe" : "/api/push/unsubscribe", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(enabled ? { token, files: ["*"] } : { token }),
  });
  if (!response.ok) throw new Error("Subscription could not be saved");
  subscribed = enabled;
  try {
    if (enabled) localStorage.setItem("hsmFcmToken", token);
    else localStorage.removeItem("hsmFcmToken");
  } catch {}
  window.dispatchEvent(new CustomEvent(HSM_EVENTS.NOTIFICATION_SUBSCRIPTION_CHANGED));
}

function syncButton() {
  button.textContent = subscribed ? "Disable push notifications" : "Enable push notifications";
}

async function update(enabled) {
  button.disabled = true;
  status.textContent = "";
  try {
    if (enabled) {
      const permission = Notification.permission === "granted" ? "granted" : await Notification.requestPermission();
      if (permission !== "granted") {
        status.textContent = "Allow notifications for this app in your device settings to subscribe.";
        return;
      }
      token ||= await messagingToken();
    }
    await setSubscription(enabled);
  } catch (error) {
    status.textContent = error.message;
  } finally {
    syncButton();
    button.disabled = false;
  }
}

async function init() {
  const installed = matchMedia("(display-mode: standalone)").matches || navigator.standalone;
  if (!installed || !("serviceWorker" in navigator) || !("PushManager" in window) || !("Notification" in window)) return;
  const response = await fetch("/api/firebase-config");
  if (!response.ok) return;
  config = await response.json();
  if (!config.apiKey || !config.vapidKey) return;
  try { token = localStorage.getItem("hsmFcmToken"); } catch {}
  if (token) {
    const current = await fetch("/api/push/subscription?token=" + encodeURIComponent(token));
    if (current.ok) subscribed = ((await current.json()).files || []).includes("*");
  }
  syncButton();
  button.hidden = false;
}

button.addEventListener("click", () => {
  if (subscribed) update(false);
  else dialog.showModal();
});
document.getElementById("notifs-push-confirm").addEventListener("click", () => {
  dialog.close();
  update(true);
});
init().catch(error => console.warn("Push subscription:", error.message));
