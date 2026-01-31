import { NextResponse } from "next/server";

/**
 * Dynamically serve the Firebase Messaging Service Worker
 * This injects environment variables at runtime, avoiding hardcoded secrets
 */
export async function GET() {
  const firebaseConfig = {
    apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY || "",
    authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN || "",
    projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID || "",
    storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET || "",
    messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID || "",
    appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID || "",
  };

  const serviceWorkerCode = `
/**
 * Firebase Cloud Messaging Service Worker
 * Handles background push notifications for web
 * Config injected at runtime from environment variables
 */

// Import Firebase scripts for Service Worker
importScripts("https://www.gstatic.com/firebasejs/10.8.0/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/10.8.0/firebase-messaging-compat.js");

// Initialize Firebase with config from server
firebase.initializeApp(${JSON.stringify(firebaseConfig)});

const messaging = firebase.messaging();

// Handle background messages
messaging.onBackgroundMessage((payload) => {
  console.log("[FCM SW] Background message received:", payload);

  const notificationTitle = payload.notification?.title || payload.data?.title || "DoneKaro";
  const notificationOptions = {
    body: payload.notification?.body || payload.data?.message || "You have a new notification",
    icon: "/android-chrome-192x192.png",
    badge: "/favicon-32x32.png",
    tag: payload.data?.notification_id || "fcm-" + Date.now(),
    renotify: true,
    requireInteraction:
      payload.data?.type === "deadline_approaching" || payload.data?.type === "deadline_passed",
    data: {
      url: payload.data?.task_id ? "/dashboard/tasks" : "/dashboard",
      notification_id: payload.data?.notification_id,
      task_id: payload.data?.task_id,
      type: payload.data?.type,
      fcm: true,
    },
    actions: payload.data?.task_id
      ? [
          { action: "view", title: "View Task" },
          { action: "dismiss", title: "Dismiss" },
        ]
      : [],
  };

  // Add urgency styling
  if (payload.data?.type === "deadline_passed") {
    notificationOptions.body = "⚠️ " + notificationOptions.body;
  } else if (payload.data?.type === "deadline_approaching") {
    notificationOptions.body = "⏰ " + notificationOptions.body;
  } else if (payload.data?.type === "task_completed") {
    notificationOptions.body = "✅ " + notificationOptions.body;
  }

  return self.registration.showNotification(notificationTitle, notificationOptions);
});

// Handle notification clicks
self.addEventListener("notificationclick", (event) => {
  console.log("[FCM SW] Notification clicked:", event.action);

  event.notification.close();

  if (event.action === "dismiss") {
    return;
  }

  const urlToOpen = event.notification.data?.url || "/dashboard";

  event.waitUntil(
    clients.matchAll({ type: "window", includeUncontrolled: true }).then((clientList) => {
      // Check if there's already a window open
      for (const client of clientList) {
        if (client.url.includes(self.registration.scope) && "focus" in client) {
          client.postMessage({
            type: "FCM_NOTIFICATION_CLICKED",
            url: urlToOpen,
            notification_id: event.notification.data?.notification_id,
          });
          return client.focus();
        }
      }

      // No window open, open a new one
      if (clients.openWindow) {
        return clients.openWindow(urlToOpen);
      }
    })
  );
});

console.log("[FCM SW] Firebase Messaging Service Worker loaded");
`;

  return new NextResponse(serviceWorkerCode, {
    headers: {
      "Content-Type": "application/javascript",
      "Service-Worker-Allowed": "/",
      "Cache-Control": "public, max-age=0, must-revalidate",
    },
  });
}
