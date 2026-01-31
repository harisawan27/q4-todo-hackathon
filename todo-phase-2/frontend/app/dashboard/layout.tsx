"use client";

import { useEffect, useRef } from "react";
import Image from "next/image";
import { useRequireAuth } from "@/lib/auth-client";
import { SidebarProvider } from "@/lib/sidebar-context";
import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";
import { initCapacitor, isNative } from "@/lib/capacitor";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isPending, isAuthenticated } = useRequireAuth();
  const fcmInitialized = useRef(false);

  // Initialize FCM when user is authenticated (only once)
  useEffect(() => {
    if (isAuthenticated && !fcmInitialized.current) {
      fcmInitialized.current = true;

      // Initialize Capacitor plugins including FCM
      initCapacitor().then(() => {
        if (isNative()) {
          console.log("[Dashboard] Capacitor initialized with FCM");
        }
      }).catch((err) => {
        console.error("[Dashboard] Failed to initialize Capacitor:", err);
      });
    }
  }, [isAuthenticated]);

  if (isPending) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <div className="inline-flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-blue-600 to-indigo-600 mb-4 overflow-hidden">
            <Image src="/logo.svg" alt="DoneKaro" width={32} height={32} className="animate-pulse" />
          </div>
          <div className="h-8 w-8 mx-auto animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
          <p className="mt-4 text-sm text-gray-500 dark:text-gray-400">Loading your workspace...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <SidebarProvider>
      <div className="flex min-h-screen bg-gray-50 dark:bg-gray-900">
        <Sidebar />
        <div className="flex flex-1 flex-col min-w-0">
          <Header />
          <main className="flex-1 overflow-auto p-4 sm:p-6">
            <div className="mx-auto max-w-6xl animate-fade-in">
              {children}
            </div>
          </main>
        </div>
      </div>
    </SidebarProvider>
  );
}
