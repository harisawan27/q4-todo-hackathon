"use client";

import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from "react";

export type Theme = "light" | "dark" | "system";
export type Language = "en" | "ur";

interface NotificationSettings {
  email: boolean;
  push: boolean;
  taskReminders: boolean;
  weeklyDigest: boolean;
}

interface Preferences {
  theme: Theme;
  language: Language;
}

interface SettingsContextType {
  notifications: NotificationSettings;
  preferences: Preferences;
  setNotificationSetting: (key: keyof NotificationSettings, value: boolean) => void;
  setPreference: <K extends keyof Preferences>(key: K, value: Preferences[K]) => void;
  resetSettings: () => void;
  effectiveTheme: "light" | "dark";
}

const defaultNotifications: NotificationSettings = {
  email: true,
  push: false,
  taskReminders: true,
  weeklyDigest: true,
};

const defaultPreferences: Preferences = {
  theme: "light",
  language: "en",
};

const SettingsContext = createContext<SettingsContextType | undefined>(undefined);

const STORAGE_KEY = "taskflow-settings";

export function SettingsProvider({ children }: { children: ReactNode }) {
  const [notifications, setNotifications] = useState<NotificationSettings>(defaultNotifications);
  const [preferences, setPreferences] = useState<Preferences>(defaultPreferences);
  const [effectiveTheme, setEffectiveTheme] = useState<"light" | "dark">("light");
  const [mounted, setMounted] = useState(false);

  // Load settings from localStorage on mount
  useEffect(() => {
    setMounted(true);
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        if (parsed.notifications) {
          setNotifications({ ...defaultNotifications, ...parsed.notifications });
        }
        if (parsed.preferences) {
          setPreferences({ ...defaultPreferences, ...parsed.preferences });
        }
      } catch (e) {
        console.error("Failed to parse settings from localStorage:", e);
      }
    }
  }, []);

  // Save settings to localStorage whenever they change
  useEffect(() => {
    if (mounted) {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({ notifications, preferences })
      );
    }
  }, [notifications, preferences, mounted]);

  // Handle theme changes
  useEffect(() => {
    if (!mounted) return;

    const updateTheme = () => {
      let theme: "light" | "dark";
      if (preferences.theme === "system") {
        theme = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
      } else {
        theme = preferences.theme;
      }
      setEffectiveTheme(theme);

      // Apply theme to document
      if (theme === "dark") {
        document.documentElement.classList.add("dark");
      } else {
        document.documentElement.classList.remove("dark");
      }
    };

    updateTheme();

    // Listen for system theme changes when using "system" preference
    if (preferences.theme === "system") {
      const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
      mediaQuery.addEventListener("change", updateTheme);
      return () => mediaQuery.removeEventListener("change", updateTheme);
    }
  }, [preferences.theme, mounted]);

  const setNotificationSetting = useCallback((key: keyof NotificationSettings, value: boolean) => {
    setNotifications((prev) => ({ ...prev, [key]: value }));
  }, []);

  const setPreference = useCallback(<K extends keyof Preferences>(key: K, value: Preferences[K]) => {
    setPreferences((prev) => ({ ...prev, [key]: value }));
  }, []);

  const resetSettings = useCallback(() => {
    setNotifications(defaultNotifications);
    setPreferences(defaultPreferences);
    localStorage.removeItem(STORAGE_KEY);
  }, []);

  return (
    <SettingsContext.Provider
      value={{
        notifications,
        preferences,
        setNotificationSetting,
        setPreference,
        resetSettings,
        effectiveTheme,
      }}
    >
      {children}
    </SettingsContext.Provider>
  );
}

export function useSettings() {
  const context = useContext(SettingsContext);
  if (context === undefined) {
    throw new Error("useSettings must be used within a SettingsProvider");
  }
  return context;
}
