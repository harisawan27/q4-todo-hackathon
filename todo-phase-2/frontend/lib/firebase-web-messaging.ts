"use client";

import { initializeApp, getApps, FirebaseApp } from "firebase/app";
import {
  getMessaging,
  getToken,
  onMessage,
  isSupported,
  Messaging,
} from "firebase/messaging";
import { apiPost, apiDelete } from "./api";
import { isNative } from "./capacitor";

/**
 * Firebase Web Messaging for Push Notifications
 * This handles FCM for web browsers (not native apps)
 */

// Firebase configuration - should match google-services.json
const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
};

let firebaseApp: FirebaseApp | null = null;
let messaging: Messaging | null = null;

/**
 * Initialize Firebase app
 */
function getFirebaseApp(): FirebaseApp | null {
  if (typeof window === "undefined") return null;

  if (firebaseApp) return firebaseApp;

  // Check if Firebase is already initialized
  if (getApps().length > 0) {
    firebaseApp = getApps()[0];
    return firebaseApp;
  }

  // Validate config
  if (!firebaseConfig.apiKey || !firebaseConfig.projectId) {
    console.warn("[Firebase Web] Missing Firebase configuration");
    return null;
  }

  try {
    firebaseApp = initializeApp(firebaseConfig);
    return firebaseApp;
  } catch (e) {
    console.error("[Firebase Web] Failed to initialize:", e);
    return null;
  }
}

/**
 * Check if Firebase Cloud Messaging is supported in this browser
 */
export async function isFirebaseMessagingSupported(): Promise<boolean> {
  // Don't use on native apps (they use Capacitor PushNotifications)
  if (isNative()) return false;

  if (typeof window === "undefined") return false;

  try {
    return await isSupported();
  } catch {
    return false;
  }
}

/**
 * Get Firebase Messaging instance
 */
async function getFirebaseMessaging(): Promise<Messaging | null> {
  if (messaging) return messaging;

  const supported = await isFirebaseMessagingSupported();
  if (!supported) return null;

  const app = getFirebaseApp();
  if (!app) return null;

  try {
    messaging = getMessaging(app);
    return messaging;
  } catch (e) {
    console.error("[Firebase Web] Failed to get messaging:", e);
    return null;
  }
}

/**
 * Request permission and get FCM token for web push
 */
export async function requestWebPushToken(): Promise<string | null> {
  const supported = await isFirebaseMessagingSupported();
  if (!supported) {
    console.log("[Firebase Web] FCM not supported in this browser");
    return null;
  }

  try {
    // Request notification permission
    const permission = await Notification.requestPermission();
    if (permission !== "granted") {
      console.log("[Firebase Web] Notification permission denied");
      return null;
    }

    const msg = await getFirebaseMessaging();
    if (!msg) return null;

    // Get the FCM token
    // Note: You need to get the VAPID key from Firebase Console > Project Settings > Cloud Messaging
    const vapidKey = process.env.NEXT_PUBLIC_FIREBASE_VAPID_KEY;

    const token = await getToken(msg, {
      vapidKey,
      serviceWorkerRegistration: await navigator.serviceWorker.register(
        "/firebase-messaging-sw.js"
      ),
    });

    console.log("[Firebase Web] FCM token obtained:", token.substring(0, 20) + "...");
    return token;
  } catch (e) {
    console.error("[Firebase Web] Failed to get token:", e);
    return null;
  }
}

/**
 * Register FCM web token with backend
 */
export async function registerWebPushToken(token: string): Promise<boolean> {
  try {
    await apiPost("/api/push/fcm/register", {
      token,
      platform: "web",
    });
    console.log("[Firebase Web] Token registered with backend");
    return true;
  } catch (e) {
    console.error("[Firebase Web] Failed to register token:", e);
    return false;
  }
}

/**
 * Unregister FCM web token from backend
 */
export async function unregisterWebPushToken(token: string): Promise<boolean> {
  try {
    await apiDelete(`/api/push/fcm/unregister?token=${encodeURIComponent(token)}`);
    console.log("[Firebase Web] Token unregistered");
    return true;
  } catch (e) {
    console.error("[Firebase Web] Failed to unregister token:", e);
    return false;
  }
}

/**
 * Set up listener for foreground messages
 */
export async function setupWebPushListener(
  onMessage: (notification: WebPushNotification) => void
): Promise<() => void> {
  const msg = await getFirebaseMessaging();
  if (!msg) return () => {};

  try {
    const { onMessage: firebaseOnMessage } = await import("firebase/messaging");

    const unsubscribe = firebaseOnMessage(msg, (payload) => {
      console.log("[Firebase Web] Foreground message received:", payload);

      onMessage({
        title: payload.notification?.title || payload.data?.title || "DoneKaro",
        body: payload.notification?.body || payload.data?.message || "",
        data: payload.data || {},
      });
    });

    return unsubscribe;
  } catch (e) {
    console.error("[Firebase Web] Failed to set up listener:", e);
    return () => {};
  }
}

/**
 * Initialize Firebase web push notifications
 * Call this when user enables push notifications
 */
export async function initFirebaseWebPush(): Promise<boolean> {
  const supported = await isFirebaseMessagingSupported();
  if (!supported) {
    console.log("[Firebase Web] Not supported");
    return false;
  }

  try {
    const token = await requestWebPushToken();
    if (!token) return false;

    // Store token locally
    localStorage.setItem("fcm_web_token", token);

    // Register with backend
    await registerWebPushToken(token);

    console.log("[Firebase Web] Initialized successfully");
    return true;
  } catch (e) {
    console.error("[Firebase Web] Failed to initialize:", e);
    return false;
  }
}

/**
 * Web push notification type
 */
export interface WebPushNotification {
  title: string;
  body: string;
  data: Record<string, string>;
}
