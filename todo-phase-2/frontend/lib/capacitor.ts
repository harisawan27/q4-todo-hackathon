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
