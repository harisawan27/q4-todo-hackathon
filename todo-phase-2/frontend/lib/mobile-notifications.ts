"use client";

import { isNative } from "./capacitor";

/**
 * Mobile Local Notifications using Capacitor Local Notifications
 * Schedules notifications on device - works even when app is closed
 * No external service (Firebase) required!
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
 * Initialize mobile notifications - request permissions and create channels
 */
export async function initMobileNotifications(): Promise<boolean> {
  if (!isNative()) return false;

  const LN = await getLocalNotifications();
  if (!LN) return false;

  try {
    // Request permission
    let permission = await LN.checkPermissions();

    if (permission.display === "prompt") {
      permission = await LN.requestPermissions();
    }

    if (permission.display !== "granted") {
      console.log("[Mobile Push] Permission not granted");
      return false;
    }

    // Create notification channels for Android
    await LN.createChannel({
      id: "deadline-reminders",
      name: "Deadline Reminders",
      description: "Notifications for upcoming task deadlines",
      importance: 5,
      sound: "default",
      vibration: true,
      lights: true,
    });

    await LN.createChannel({
      id: "task-updates",
      name: "Task Updates",
      description: "General task notifications",
      importance: 3,
      sound: "default",
      vibration: true,
    });

    console.log("[Mobile Push] Initialized successfully");
    return true;
  } catch (e) {
    console.error("[Mobile Push] Failed to initialize:", e);
    return false;
  }
}

/**
 * Generate a numeric ID from a string (for notification IDs)
 */
function hashStringToId(str: string, suffix: number = 0): number {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return Math.abs(hash + suffix);
}

/**
 * Schedule deadline reminder notifications for a task
 * Schedules: 24h, 12h, 6h, 3h, 1h before, and at deadline
 */
export async function scheduleTaskReminders(
  taskId: string,
  taskTitle: string,
  dueDate: string,
  dueTime: string | null
): Promise<boolean> {
  if (!isNative()) return false;

  const LN = await getLocalNotifications();
  if (!LN) return false;

  try {
    // Parse the due date/time (stored as UTC)
    const deadline = dueTime
      ? new Date(`${dueDate}T${dueTime}Z`)
      : new Date(`${dueDate}T23:59:59Z`);

    const now = new Date();
    const notifications: Array<{
      id: number;
      title: string;
      body: string;
      schedule: { at: Date };
      channelId: string;
      extra: { task_id: string };
    }> = [];

    // 24 hours before
    const reminder24h = new Date(deadline.getTime() - 24 * 60 * 60 * 1000);
    if (reminder24h > now) {
      notifications.push({
        id: hashStringToId(taskId, 1),
        title: "Task Due Tomorrow",
        body: `"${taskTitle}" is due in 24 hours`,
        schedule: { at: reminder24h },
        channelId: "deadline-reminders",
        extra: { task_id: taskId },
      });
    }

    // 12 hours before
    const reminder12h = new Date(deadline.getTime() - 12 * 60 * 60 * 1000);
    if (reminder12h > now) {
      notifications.push({
        id: hashStringToId(taskId, 2),
        title: "Task Due Today",
        body: `"${taskTitle}" is due in 12 hours`,
        schedule: { at: reminder12h },
        channelId: "deadline-reminders",
        extra: { task_id: taskId },
      });
    }

    // 6 hours before
    const reminder6h = new Date(deadline.getTime() - 6 * 60 * 60 * 1000);
    if (reminder6h > now) {
      notifications.push({
        id: hashStringToId(taskId, 3),
        title: "Task Due Soon",
        body: `"${taskTitle}" is due in 6 hours`,
        schedule: { at: reminder6h },
        channelId: "deadline-reminders",
        extra: { task_id: taskId },
      });
    }

    // 3 hours before
    const reminder3h = new Date(deadline.getTime() - 3 * 60 * 60 * 1000);
    if (reminder3h > now) {
      notifications.push({
        id: hashStringToId(taskId, 4),
        title: "Task Due Soon!",
        body: `"${taskTitle}" is due in 3 hours`,
        schedule: { at: reminder3h },
        channelId: "deadline-reminders",
        extra: { task_id: taskId },
      });
    }

    // 1 hour before
    const reminder1h = new Date(deadline.getTime() - 60 * 60 * 1000);
    if (reminder1h > now) {
      notifications.push({
        id: hashStringToId(taskId, 5),
        title: "Task Due Very Soon!",
        body: `"${taskTitle}" is due in 1 hour`,
        schedule: { at: reminder1h },
        channelId: "deadline-reminders",
        extra: { task_id: taskId },
      });
    }

    // At deadline
    if (deadline > now) {
      notifications.push({
        id: hashStringToId(taskId, 6),
        title: "Task Deadline!",
        body: `"${taskTitle}" is due now!`,
        schedule: { at: deadline },
        channelId: "deadline-reminders",
        extra: { task_id: taskId },
      });
    }

    if (notifications.length > 0) {
      await LN.schedule({ notifications });
      console.log(`[Mobile Push] Scheduled ${notifications.length} reminders for task: ${taskTitle}`);
    }

    return true;
  } catch (e) {
    console.error("[Mobile Push] Failed to schedule reminders:", e);
    return false;
  }
}

/**
 * Cancel all scheduled reminders for a task
 * Call this when task is completed or deleted
 */
export async function cancelTaskReminders(taskId: string): Promise<boolean> {
  if (!isNative()) return false;

  const LN = await getLocalNotifications();
  if (!LN) return false;

  try {
    // Cancel all 6 possible reminders for this task (24h, 12h, 6h, 3h, 1h, deadline)
    await LN.cancel({
      notifications: [
        { id: hashStringToId(taskId, 1) },
        { id: hashStringToId(taskId, 2) },
        { id: hashStringToId(taskId, 3) },
        { id: hashStringToId(taskId, 4) },
        { id: hashStringToId(taskId, 5) },
        { id: hashStringToId(taskId, 6) },
      ],
    });
    console.log(`[Mobile Push] Cancelled reminders for task: ${taskId}`);
    return true;
  } catch (e) {
    console.error("[Mobile Push] Failed to cancel reminders:", e);
    return false;
  }
}

/**
 * Show an immediate notification (for in-app events)
 */
export async function showImmediateNotification(
  id: string,
  title: string,
  body: string,
  taskId?: string
): Promise<boolean> {
  if (!isNative()) return false;

  const LN = await getLocalNotifications();
  if (!LN) return false;

  try {
    await LN.schedule({
      notifications: [
        {
          id: hashStringToId(id),
          title,
          body,
          channelId: "task-updates",
          extra: taskId ? { task_id: taskId } : {},
        },
      ],
    });
    return true;
  } catch (e) {
    console.error("[Mobile Push] Failed to show notification:", e);
    return false;
  }
}

/**
 * Set up listener for notification taps
 */
export async function setupMobileNotificationListeners(
  onNotificationTapped: (taskId: string | null) => void
): Promise<() => void> {
  if (!isNative()) return () => {};

  const LN = await getLocalNotifications();
  if (!LN) return () => {};

  try {
    const listener = await LN.addListener(
      "localNotificationActionPerformed",
      (action) => {
        const taskId = action.notification.extra?.task_id || null;
        onNotificationTapped(taskId);
      }
    );

    return () => listener.remove();
  } catch (e) {
    console.error("[Mobile Push] Failed to set up listeners:", e);
    return () => {};
  }
}

/**
 * Check if notifications are enabled
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
