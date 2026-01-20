"use client";

import { apiPost, apiDelete, apiGet } from "./api";

/**
 * Check if push notifications are supported in the current browser
 */
export function isPushSupported(): boolean {
  return (
    typeof window !== "undefined" &&
    "serviceWorker" in navigator &&
    "PushManager" in window &&
    "Notification" in window
  );
}

/**
 * Get the current notification permission status
 */
export function getNotificationPermission(): NotificationPermission | "unsupported" {
  if (!isPushSupported()) return "unsupported";
  return Notification.permission;
}

/**
 * Request notification permission from the user
 */
export async function requestNotificationPermission(): Promise<
  NotificationPermission | "unsupported"
> {
  if (!isPushSupported()) return "unsupported";

  const permission = await Notification.requestPermission();
  return permission;
}

/**
 * Convert a base64 string to a Uint8Array for VAPID key
 */
function urlBase64ToUint8Array(base64String: string): Uint8Array {
  const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }

  return outputArray;
}

/**
 * Get VAPID public key from backend
 */
async function getVapidPublicKey(): Promise<string | null> {
  try {
    const response = await apiGet<{ vapid_public_key: string; push_enabled: boolean }>(
      "/api/push/vapid-key"
    );
    if (!response.push_enabled || !response.vapid_public_key) {
      return null;
    }
    return response.vapid_public_key;
  } catch (error) {
    console.error("[Push] Failed to get VAPID key:", error);
    return null;
  }
}

/**
 * Register service worker and subscribe to push notifications
 */
export async function registerPushNotifications(): Promise<boolean> {
  if (!isPushSupported()) {
    console.log("[Push] Push notifications not supported");
    return false;
  }

  // Check permission
  const permission = await requestNotificationPermission();
  if (permission !== "granted") {
    console.log("[Push] Notification permission not granted:", permission);
    return false;
  }

  try {
    // Register service worker
    const registration = await navigator.serviceWorker.register("/sw.js", {
      scope: "/",
    });
    console.log("[Push] Service Worker registered:", registration.scope);

    // Wait for service worker to be ready
    await navigator.serviceWorker.ready;

    // Get VAPID key from backend
    const vapidPublicKey = await getVapidPublicKey();
    if (!vapidPublicKey) {
      console.log("[Push] Push notifications not configured on server");
      return false;
    }

    // Check for existing subscription
    let subscription = await registration.pushManager.getSubscription();

    // If no subscription, create one
    if (!subscription) {
      subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(vapidPublicKey),
      });
      console.log("[Push] New push subscription created");
    }

    // Send subscription to backend
    const subscriptionJson = subscription.toJSON();
    await apiPost("/api/push/subscribe", {
      endpoint: subscriptionJson.endpoint,
      keys: subscriptionJson.keys,
    });

    console.log("[Push] Subscription registered with backend");
    return true;
  } catch (error) {
    console.error("[Push] Failed to register push notifications:", error);
    return false;
  }
}

/**
 * Unsubscribe from push notifications
 */
export async function unsubscribePushNotifications(): Promise<boolean> {
  if (!isPushSupported()) return false;

  try {
    const registration = await navigator.serviceWorker.getRegistration();
    if (!registration) return false;

    const subscription = await registration.pushManager.getSubscription();
    if (!subscription) return false;

    // Unsubscribe from push manager
    await subscription.unsubscribe();

    // Remove subscription from backend
    await apiDelete(
      `/api/push/unsubscribe?endpoint=${encodeURIComponent(subscription.endpoint)}`
    );

    console.log("[Push] Unsubscribed from push notifications");
    return true;
  } catch (error) {
    console.error("[Push] Failed to unsubscribe:", error);
    return false;
  }
}

/**
 * Check if push notifications are currently enabled for this browser
 */
export async function isPushEnabled(): Promise<boolean> {
  if (!isPushSupported()) return false;
  if (Notification.permission !== "granted") return false;

  try {
    const registration = await navigator.serviceWorker.getRegistration();
    if (!registration) return false;

    const subscription = await registration.pushManager.getSubscription();
    return !!subscription;
  } catch {
    return false;
  }
}

/**
 * Set up message listener for service worker messages
 */
export function setupPushMessageListener(
  onNewNotification: () => void,
  onNotificationClicked?: (url: string) => void
): () => void {
  if (!isPushSupported()) return () => {};

  const handler = (event: MessageEvent) => {
    if (event.data?.type === "NEW_NOTIFICATION") {
      onNewNotification();
    } else if (event.data?.type === "NOTIFICATION_CLICKED" && onNotificationClicked) {
      onNotificationClicked(event.data.url);
    }
  };

  navigator.serviceWorker.addEventListener("message", handler);

  // Return cleanup function
  return () => {
    navigator.serviceWorker.removeEventListener("message", handler);
  };
}
