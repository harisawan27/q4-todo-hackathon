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

  // Initialize mobile notifications
  try {
    const { initMobileNotifications } = await import("./mobile-notifications");
    await initMobileNotifications();
  } catch (e) {
    console.error("Failed to init mobile notifications:", e);
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
