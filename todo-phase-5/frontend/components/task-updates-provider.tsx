"use client";

import { useTaskUpdates } from "@/lib/sse-client";

interface TaskUpdatesProviderProps {
  userId: string | null;
  children: React.ReactNode;
}

export function TaskUpdatesProvider({ userId, children }: TaskUpdatesProviderProps) {
  useTaskUpdates(userId);
  return <>{children}</>;
}
