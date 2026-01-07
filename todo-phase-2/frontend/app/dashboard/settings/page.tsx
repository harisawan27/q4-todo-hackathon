"use client";

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import { useToast } from "@/components/ui/toast";
import { useSettings, Theme, Language } from "@/lib/settings-context";
import { apiGet, apiDelete } from "@/lib/api";
import type { Task } from "@/types/task";

const TIMEZONES = [
  { value: "UTC", label: "UTC" },
  { value: "America/New_York", label: "Eastern Time (US)" },
  { value: "America/Chicago", label: "Central Time (US)" },
  { value: "America/Denver", label: "Mountain Time (US)" },
  { value: "America/Los_Angeles", label: "Pacific Time (US)" },
  { value: "Europe/London", label: "London" },
  { value: "Europe/Paris", label: "Paris" },
  { value: "Europe/Berlin", label: "Berlin" },
  { value: "Asia/Tokyo", label: "Tokyo" },
  { value: "Asia/Shanghai", label: "Shanghai" },
  { value: "Asia/Kolkata", label: "India (IST)" },
  { value: "Australia/Sydney", label: "Sydney" },
];

const LANGUAGES = [
  { value: "en", label: "English" },
  { value: "ur", label: "Urdu (اردو)" },
];

export default function SettingsPage() {
  const { notifications, preferences, setNotificationSetting, setPreference, resetSettings } = useSettings();
  const toast = useToast();
  const queryClient = useQueryClient();
  const [showClearDialog, setShowClearDialog] = useState(false);
  const [showResetDialog, setShowResetDialog] = useState(false);

  const clearDataMutation = useMutation({
    mutationFn: async () => {
      const tasks = await apiGet<Task[]>("/api/tasks");
      await Promise.all(tasks.map((task) => apiDelete(`/api/tasks/${task.id}`)));
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      toast.success("Data cleared", "All your tasks have been deleted");
      setShowClearDialog(false);
    },
    onError: () => {
      toast.error("Failed to clear data", "Please try again");
    },
  });

  const handleExport = async () => {
    try {
      const tasks = await apiGet<Task[]>("/api/tasks");
      const data = {
        exportedAt: new Date().toISOString(),
        settings: { notifications, preferences },
        tasks,
      };

      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `taskflow-export-${new Date().toISOString().split("T")[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      toast.success("Export successful", "Your data has been downloaded");
    } catch {
      toast.error("Export failed", "Could not export your data");
    }
  };

  const handleResetSettings = () => {
    resetSettings();
    toast.success("Settings reset", "All settings have been restored to defaults");
    setShowResetDialog(false);
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Settings</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Manage your preferences and account settings</p>
      </div>

      {/* Notifications Settings */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <div className="rounded-lg bg-blue-100 dark:bg-blue-900/30 p-2">
              <svg className="h-5 w-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white">Notifications</h3>
              <p className="text-xs text-gray-500 dark:text-gray-400">Configure how you receive notifications</p>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 rounded-lg border border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
              <div>
                <p className="text-sm font-medium text-gray-900 dark:text-white">Email Notifications</p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Receive notifications via email</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={notifications.email}
                  onChange={(e) => setNotificationSetting("email", e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 dark:bg-gray-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-100 dark:peer-focus:ring-blue-900 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>

            <div className="flex items-center justify-between p-4 rounded-lg border border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
              <div>
                <p className="text-sm font-medium text-gray-900 dark:text-white">Push Notifications</p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Receive push notifications in browser</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={notifications.push}
                  onChange={(e) => setNotificationSetting("push", e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 dark:bg-gray-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-100 dark:peer-focus:ring-blue-900 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>

            <div className="flex items-center justify-between p-4 rounded-lg border border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
              <div>
                <p className="text-sm font-medium text-gray-900 dark:text-white">Task Reminders</p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Get reminded about upcoming due dates</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={notifications.taskReminders}
                  onChange={(e) => setNotificationSetting("taskReminders", e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 dark:bg-gray-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-100 dark:peer-focus:ring-blue-900 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>

            <div className="flex items-center justify-between p-4 rounded-lg border border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
              <div>
                <p className="text-sm font-medium text-gray-900 dark:text-white">Weekly Digest</p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Get a weekly summary of your tasks</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={notifications.weeklyDigest}
                  onChange={(e) => setNotificationSetting("weeklyDigest", e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 dark:bg-gray-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-100 dark:peer-focus:ring-blue-900 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Appearance Settings */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <div className="rounded-lg bg-purple-100 dark:bg-purple-900/30 p-2">
              <svg className="h-5 w-5 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
              </svg>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white">Appearance</h3>
              <p className="text-xs text-gray-500 dark:text-gray-400">Customize how TaskFlow looks</p>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Theme</label>
              <div className="grid grid-cols-3 gap-3">
                {(["light", "dark", "system"] as const).map((theme) => (
                  <button
                    key={theme}
                    onClick={() => setPreference("theme", theme as Theme)}
                    className={`p-3 rounded-lg border-2 transition-all ${
                      preferences.theme === theme
                        ? "border-blue-500 bg-blue-50 dark:bg-blue-900/30"
                        : "border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600"
                    }`}
                  >
                    <div className="flex flex-col items-center gap-2">
                      {theme === "light" && (
                        <svg className="h-6 w-6 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                        </svg>
                      )}
                      {theme === "dark" && (
                        <svg className="h-6 w-6 text-indigo-600 dark:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                        </svg>
                      )}
                      {theme === "system" && (
                        <svg className="h-6 w-6 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                        </svg>
                      )}
                      <span className="text-xs font-medium text-gray-700 dark:text-gray-300 capitalize">{theme}</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Language</label>
                <select
                  value={preferences.language}
                  onChange={(e) => setPreference("language", e.target.value as Language)}
                  className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-2.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:text-white"
                >
                  {LANGUAGES.map((lang) => (
                    <option key={lang.value} value={lang.value}>
                      {lang.label}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Timezone</label>
                <select
                  value={preferences.timezone}
                  onChange={(e) => setPreference("timezone", e.target.value)}
                  className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-2.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:text-white"
                >
                  {TIMEZONES.map((tz) => (
                    <option key={tz.value} value={tz.value}>
                      {tz.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Data & Privacy */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <div className="rounded-lg bg-green-100 dark:bg-green-900/30 p-2">
              <svg className="h-5 w-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white">Data & Privacy</h3>
              <p className="text-xs text-gray-500 dark:text-gray-400">Manage your data and privacy settings</p>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 p-4 rounded-lg border border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
              <div>
                <p className="text-sm font-medium text-gray-900 dark:text-white">Export Data</p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Download a copy of all your data</p>
              </div>
              <Button variant="outline" onClick={handleExport} className="shrink-0">
                <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Export
              </Button>
            </div>

            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 p-4 rounded-lg border border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
              <div>
                <p className="text-sm font-medium text-gray-900 dark:text-white">Reset Settings</p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Restore all settings to defaults</p>
              </div>
              <Button variant="outline" onClick={() => setShowResetDialog(true)} className="shrink-0">
                <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Reset
              </Button>
            </div>

            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 p-4 rounded-lg border border-red-100 dark:border-red-900/50 bg-red-50/50 dark:bg-red-900/10">
              <div>
                <p className="text-sm font-medium text-gray-900 dark:text-white">Clear All Data</p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Delete all your tasks permanently</p>
              </div>
              <Button
                variant="outline"
                onClick={() => setShowClearDialog(true)}
                className="shrink-0 text-red-600 border-red-200 hover:bg-red-50 dark:border-red-800 dark:hover:bg-red-900/20"
              >
                <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Clear Data
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Settings are auto-saved notice */}
      <div className="flex items-center justify-center gap-2 text-sm text-gray-500 dark:text-gray-400">
        <svg className="h-4 w-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
        Settings are saved automatically
      </div>

      {/* Clear Data Confirmation Dialog */}
      <ConfirmDialog
        isOpen={showClearDialog}
        onClose={() => setShowClearDialog(false)}
        onConfirm={() => clearDataMutation.mutate()}
        title="Clear All Data"
        message="Are you sure you want to delete all your tasks? This action cannot be undone."
        confirmText="Clear All Data"
        cancelText="Cancel"
        variant="danger"
        isLoading={clearDataMutation.isPending}
      />

      {/* Reset Settings Confirmation Dialog */}
      <ConfirmDialog
        isOpen={showResetDialog}
        onClose={() => setShowResetDialog(false)}
        onConfirm={handleResetSettings}
        title="Reset Settings"
        message="Are you sure you want to reset all settings to their default values?"
        confirmText="Reset Settings"
        cancelText="Cancel"
        variant="danger"
      />
    </div>
  );
}
