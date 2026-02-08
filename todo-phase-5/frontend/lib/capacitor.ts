"use client";

import { Capacitor } from "@capacitor/core";
import { Browser } from "@capacitor/browser";
import { App } from "@capacitor/app";

export const isNative = (): boolean => {
  return Capacitor.isNativePlatform();
};

export const isAndroid = (): boolean => {
  return Capacitor.getPlatform() === "android";
};

export const isIOS = (): boolean => {
  return Capacitor.getPlatform() === "ios";
};

/**
 * Initialize all Capacitor plugins and listeners
 * Call this once when the app starts
 */
export async function initCapacitor(): Promise<void> {
  if (!isNative()) return;

  // Initialize local notifications (for scheduled reminders)
  try {
    const { initMobileNotifications } = await import("./mobile-notifications");
    await initMobileNotifications();
  } catch (e) {
    console.error("Failed to init mobile notifications:", e);
  }

  // Initialize FCM push notifications (for server-sent notifications)
  try {
    const {
      initFCMPushNotifications,
      setupFCMListeners,
      createDefaultChannels,
      registerFCMTokenWithBackend,
    } = await import("./fcm-notifications");

    // Create notification channels first (Android 8.0+)
    await createDefaultChannels();

    // Initialize FCM
    const initialized = await initFCMPushNotifications();
    if (!initialized) {
      console.log("[Capacitor] FCM initialization skipped or failed");
      return;
    }

    // Set up FCM event listeners
    await setupFCMListeners({
      onRegistration: async (token) => {
        console.log("[Capacitor] FCM token received, registering with backend...");
        // Store token for later use
        localStorage.setItem("fcm_token", token);
        // Register with backend
        await registerFCMTokenWithBackend(token);
      },
      onRegistrationError: (error) => {
        console.error("[Capacitor] FCM registration error:", error);
      },
      onPushReceived: (notification) => {
        console.log("[Capacitor] Push notification received in foreground:", notification);
        // The notification will be displayed automatically by the system
        // You can add custom handling here if needed
      },
      onPushTapped: (notification) => {
        console.log("[Capacitor] Push notification tapped:", notification);
        // Navigate to relevant page based on notification data
        if (notification.data?.task_id) {
          window.location.href = "/dashboard/tasks";
        } else {
          window.location.href = "/dashboard";
        }
      },
    });

    console.log("[Capacitor] FCM push notifications initialized successfully");
  } catch (e) {
    console.error("Failed to init FCM push notifications:", e);
  }
}

const APP_URL = "https://q4-todo-hackathon.vercel.app";

export async function openOAuthInBrowser(provider: string): Promise<void> {
  const callbackUrl = `${APP_URL}/dashboard`;
  const authUrl = `${APP_URL}/api/auth/signin/social?provider=${provider}&callbackURL=${encodeURIComponent(callbackUrl)}`;

  // Listen for the browser to finish (when redirected back)
  const browserFinishHandler = await Browser.addListener("browserFinished", () => {
    // Reload the page to pick up the new session
    window.location.href = `${APP_URL}/dashboard`;
    browserFinishHandler.remove();
  });

  // Open OAuth in Chrome Custom Tab (better UX than external browser)
  await Browser.open({
    url: authUrl,
    presentationStyle: "popover",
  });
}

export async function closeBrowser(): Promise<void> {
  try {
    await Browser.close();
  } catch {
    // Browser might already be closed
  }
}

// Listen for app URL open events (deep links)
export function setupDeepLinkListener(callback: (url: string) => void): void {
  if (!isNative()) return;

  App.addListener("appUrlOpen", (event: { url: string }) => {
    // Close the browser if open
    closeBrowser();
    callback(event.url);
  });
}
