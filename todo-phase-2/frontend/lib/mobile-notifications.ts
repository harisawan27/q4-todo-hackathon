"use client";

import { isNative } from "./capacitor";
import type { Notification } from "./notifications";

/**
 * Dynamic import for Capacitor Local Notifications
 * Only loaded on native platforms to avoid build errors on web
 */
let LocalNotifications: typeof import("@capacitor/local-notifications").LocalNotifications | null = null;

async function getLocalNotifications() {
  if (!isNative()) return null;

  if (!LocalNotifications) {
    try {
      const module = await import("@capacitor/local-notifications");
      LocalNotifications = module.LocalNotifications;
    } catch (e) {
      console.error("[Mobile Push] Failed to load LocalNotifications:", e);
      return null;
    }
  }

  return LocalNotifications;
}

/**
 * Convert notification ID (UUID) to a numeric ID for Capacitor
 */
function hashNotificationId(id: string): number {
  let hash = 0;
  for (let i = 0; i < id.length; i++) {
    const char = id.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32bit integer
  }
  return Math.abs(hash);
}

/**
 * Initialize mobile notifications
 * Sets up notification channel and requests permissions
 */
export async function initMobileNotifications(): Promise<boolean> {
  if (!isNative()) return false;

  const LN = await getLocalNotifications();
  if (!LN) return false;

  try {
    // Request permission
    const permission = await LN.requestPermissions();
    if (permission.display !== "granted") {
      console.log("[Mobile Push] Permission not granted");
      return false;
    }

    // Create notification channel for Android
    await LN.createChannel({
      id: "deadline-reminders",
      name: "Deadline Reminders",
      description: "Notifications for upcoming task deadlines",
      importance: 5, // Max importance (sound + vibration + heads-up)
      sound: "default",
      vibration: true,
      lights: true,
      lightColor: "#3b82f6",
    });

    // Create a general channel
    await LN.createChannel({
      id: "general",
      name: "General Notifications",
      description: "General app notifications",
      importance: 3, // Default importance
      sound: "default",
      vibration: true,
    });

    console.log("[Mobile Push] Mobile notifications initialized");
    return true;
  } catch (e) {
    console.error("[Mobile Push] Failed to initialize:", e);
    return false;
  }
}

/**
 * Show a local notification on mobile device
 */
export async function showMobileNotification(notification: Notification): Promise<boolean> {
  if (!isNative()) return false;

  const LN = await getLocalNotifications();
  if (!LN) return false;

  try {
    const isDeadline =
      notification.type === "deadline_approaching" ||
      notification.type === "deadline_passed";

    await LN.schedule({
      notifications: [
        {
          id: hashNotificationId(notification.id),
          title: notification.title,
          body: notification.message,
          channelId: isDeadline ? "deadline-reminders" : "general",
          smallIcon: "ic_notification",
          largeIcon: "ic_launcher",
          sound: "default",
          extra: {
            notification_id: notification.id,
            task_id: notification.task_id,
            type: notification.type,
          },
        },
      ],
    });

    console.log("[Mobile Push] Notification shown:", notification.title);
    return true;
  } catch (e) {
    console.error("[Mobile Push] Failed to show notification:", e);
    return false;
  }
}

/**
 * Set up listener for notification actions (tap, dismiss)
 */
export async function setupMobileNotificationListeners(
  onTap: (taskId: string | null) => void
): Promise<() => void> {
  if (!isNative()) return () => {};

  const LN = await getLocalNotifications();
  if (!LN) return () => {};

  try {
    const listener = await LN.addListener(
      "localNotificationActionPerformed",
      (action) => {
        const taskId = action.notification.extra?.task_id || null;
        onTap(taskId);
      }
    );

    return () => {
      listener.remove();
    };
  } catch (e) {
    console.error("[Mobile Push] Failed to set up listeners:", e);
    return () => {};
  }
}

/**
 * Check if mobile notifications are enabled
 */
export async function isMobileNotificationsEnabled(): Promise<boolean> {
  if (!isNative()) return false;

  const LN = await getLocalNotifications();
  if (!LN) return false;

  try {
    const permission = await LN.checkPermissions();
    return permission.display === "granted";
  } catch {
    return false;
  }
}

/**
 * Cancel all pending notifications
 */
export async function cancelAllMobileNotifications(): Promise<void> {
  if (!isNative()) return;

  const LN = await getLocalNotifications();
  if (!LN) return;

  try {
    const pending = await LN.getPending();
    if (pending.notifications.length > 0) {
      await LN.cancel({
        notifications: pending.notifications.map((n) => ({ id: n.id })),
      });
    }
  } catch (e) {
    console.error("[Mobile Push] Failed to cancel notifications:", e);
  }
}
