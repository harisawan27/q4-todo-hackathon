"use client";

import { isNative, isAndroid } from "./capacitor";
import { apiPost, apiDelete } from "./api";

/**
 * Firebase Cloud Messaging (FCM) Push Notifications for Native Apps
 * Uses Capacitor PushNotifications plugin which interfaces with FCM on Android
 */

let PushNotifications: typeof import("@capacitor/push-notifications").PushNotifications | null =
  null;

async function getPushNotifications() {
  if (!isNative()) return null;

  if (!PushNotifications) {
    try {
      const module = await import("@capacitor/push-notifications");
      PushNotifications = module.PushNotifications;
    } catch (e) {
      console.error("[FCM] Failed to load PushNotifications:", e);
      return null;
    }
  }

  return PushNotifications;
}

/**
 * Check if FCM push notifications are supported
 */
export function isFCMSupported(): boolean {
  return isNative() && isAndroid();
}

/**
 * Initialize FCM push notifications
 * Requests permission and registers for push notifications
 */
export async function initFCMPushNotifications(): Promise<boolean> {
  if (!isFCMSupported()) {
    console.log("[FCM] Not supported on this platform");
    return false;
  }

  const PN = await getPushNotifications();
  if (!PN) return false;

  try {
    // Check permissions
    let permStatus = await PN.checkPermissions();
    console.log("[FCM] Current permission status:", permStatus.receive);

    if (permStatus.receive === "prompt") {
      permStatus = await PN.requestPermissions();
    }

    if (permStatus.receive !== "granted") {
      console.log("[FCM] Permission not granted:", permStatus.receive);
      return false;
    }

    // Register with FCM
    await PN.register();
    console.log("[FCM] Registered for push notifications");

    return true;
  } catch (e) {
    console.error("[FCM] Failed to initialize:", e);
    return false;
  }
}

/**
 * Set up FCM event listeners
 * Call this once when the app initializes
 */
export async function setupFCMListeners(handlers: {
  onRegistration?: (token: string) => void;
  onRegistrationError?: (error: Error) => void;
  onPushReceived?: (notification: FCMNotification) => void;
  onPushTapped?: (notification: FCMNotification) => void;
}): Promise<() => void> {
  if (!isFCMSupported()) return () => {};

  const PN = await getPushNotifications();
  if (!PN) return () => {};

  const listeners: Array<{ remove: () => Promise<void> }> = [];

  try {
    // Registration success - called when FCM token is received
    const registrationListener = await PN.addListener("registration", (token) => {
      console.log("[FCM] Registration token received:", token.value.substring(0, 20) + "...");
      handlers.onRegistration?.(token.value);
    });
    listeners.push(registrationListener);

    // Registration error
    const errorListener = await PN.addListener("registrationError", (error) => {
      console.error("[FCM] Registration error:", error);
      handlers.onRegistrationError?.(new Error(error.error));
    });
    listeners.push(errorListener);

    // Push notification received (foreground)
    const receivedListener = await PN.addListener(
      "pushNotificationReceived",
      (notification) => {
        console.log("[FCM] Push received:", notification);
        handlers.onPushReceived?.({
          id: notification.id,
          title: notification.title || "DoneKaro",
          body: notification.body || "",
          data: notification.data || {},
        });
      }
    );
    listeners.push(receivedListener);

    // Push notification tapped (user interaction)
    const actionListener = await PN.addListener(
      "pushNotificationActionPerformed",
      (action) => {
        console.log("[FCM] Push tapped:", action);
        handlers.onPushTapped?.({
          id: action.notification.id,
          title: action.notification.title || "DoneKaro",
          body: action.notification.body || "",
          data: action.notification.data || {},
        });
      }
    );
    listeners.push(actionListener);

    console.log("[FCM] Listeners set up successfully");

    // Return cleanup function
    return () => {
      listeners.forEach((listener) => listener.remove());
    };
  } catch (e) {
    console.error("[FCM] Failed to set up listeners:", e);
    return () => {};
  }
}

/**
 * Register FCM token with backend for server-sent push notifications
 */
export async function registerFCMTokenWithBackend(token: string): Promise<boolean> {
  try {
    await apiPost("/api/push/fcm/register", {
      token,
      platform: "android",
    });
    console.log("[FCM] Token registered with backend");
    return true;
  } catch (e) {
    console.error("[FCM] Failed to register token with backend:", e);
    return false;
  }
}

/**
 * Unregister FCM token from backend
 */
export async function unregisterFCMToken(token: string): Promise<boolean> {
  try {
    await apiDelete(`/api/push/fcm/unregister?token=${encodeURIComponent(token)}`);
    console.log("[FCM] Token unregistered from backend");
    return true;
  } catch (e) {
    console.error("[FCM] Failed to unregister token:", e);
    return false;
  }
}

/**
 * Get list of delivered notifications (Android only)
 */
export async function getDeliveredNotifications(): Promise<FCMNotification[]> {
  if (!isFCMSupported()) return [];

  const PN = await getPushNotifications();
  if (!PN) return [];

  try {
    const result = await PN.getDeliveredNotifications();
    return result.notifications.map((n) => ({
      id: n.id,
      title: n.title || "",
      body: n.body || "",
      data: n.data || {},
    }));
  } catch (e) {
    console.error("[FCM] Failed to get delivered notifications:", e);
    return [];
  }
}

/**
 * Remove all delivered notifications
 */
export async function removeAllDeliveredNotifications(): Promise<boolean> {
  if (!isFCMSupported()) return false;

  const PN = await getPushNotifications();
  if (!PN) return false;

  try {
    await PN.removeAllDeliveredNotifications();
    console.log("[FCM] All delivered notifications removed");
    return true;
  } catch (e) {
    console.error("[FCM] Failed to remove notifications:", e);
    return false;
  }
}

/**
 * Create a notification channel (Android 8.0+)
 */
export async function createNotificationChannel(
  id: string,
  name: string,
  description: string,
  importance: 1 | 2 | 3 | 4 | 5 = 4
): Promise<boolean> {
  if (!isFCMSupported()) return false;

  const PN = await getPushNotifications();
  if (!PN) return false;

  try {
    await PN.createChannel({
      id,
      name,
      description,
      importance,
      sound: "default",
      vibration: true,
      lights: true,
    });
    console.log(`[FCM] Channel created: ${id}`);
    return true;
  } catch (e) {
    console.error("[FCM] Failed to create channel:", e);
    return false;
  }
}

/**
 * Create default notification channels for the app
 */
export async function createDefaultChannels(): Promise<void> {
  await createNotificationChannel(
    "deadline-alerts",
    "Deadline Alerts",
    "Important alerts for upcoming and overdue task deadlines",
    5 // Max importance
  );

  await createNotificationChannel(
    "task-updates",
    "Task Updates",
    "General updates about your tasks",
    3 // Default importance
  );

  await createNotificationChannel(
    "reminders",
    "Reminders",
    "Scheduled task reminders",
    4 // High importance
  );
}

/**
 * FCM Notification type
 */
export interface FCMNotification {
  id: string;
  title: string;
  body: string;
  data: Record<string, string>;
}
