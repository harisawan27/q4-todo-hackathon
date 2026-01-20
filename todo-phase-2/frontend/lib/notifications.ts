"use client";

import { apiGet, apiPatch, apiPost, apiDelete } from "./api";
import { formatRelativeTime } from "./date-utils";

export interface Notification {
  id: string;
  user_id: string;
  title: string;
  message: string;
  type: NotificationType;
  task_id: string | null;
  read: boolean;
  created_at: string;
}

export type NotificationType =
  | "task_created"
  | "task_completed"
  | "task_deleted"
  | "deadline_approaching"
  | "deadline_passed"
  | "system";

export interface UnreadCountResponse {
  unread_count: number;
}

export interface MarkAllReadResponse {
  marked_read: number;
}

export interface ClearResponse {
  deleted: number;
}

// API functions
export async function getNotifications(unreadOnly = false, limit = 50): Promise<Notification[]> {
  const params = new URLSearchParams();
  if (unreadOnly) params.append("unread_only", "true");
  if (limit) params.append("limit", limit.toString());
  const queryString = params.toString();
  return apiGet<Notification[]>(`/api/notifications${queryString ? `?${queryString}` : ""}`);
}

export async function getUnreadCount(): Promise<UnreadCountResponse> {
  return apiGet<UnreadCountResponse>("/api/notifications/unread-count");
}

export async function markNotificationAsRead(notificationId: string): Promise<Notification> {
  return apiPatch<Notification>(`/api/notifications/${notificationId}`, { read: true });
}

export async function markAllNotificationsAsRead(): Promise<MarkAllReadResponse> {
  return apiPost<MarkAllReadResponse>("/api/notifications/mark-all-read");
}

export async function deleteNotification(notificationId: string): Promise<void> {
  return apiDelete<void>(`/api/notifications/${notificationId}`);
}

export async function clearAllNotifications(readOnly = false): Promise<ClearResponse> {
  const params = readOnly ? "?read_only=true" : "";
  return apiDelete<ClearResponse>(`/api/notifications${params}`);
}

// Helper function to get notification icon based on type
export function getNotificationIcon(type: NotificationType): string {
  switch (type) {
    case "task_created":
      return "plus-circle";
    case "task_completed":
      return "check-circle";
    case "task_deleted":
      return "trash";
    case "deadline_approaching":
      return "clock";
    case "deadline_passed":
      return "exclamation-circle";
    case "system":
    default:
      return "bell";
  }
}

// Helper function to get notification color based on type
export function getNotificationColor(type: NotificationType): string {
  switch (type) {
    case "task_created":
      return "text-green-500";
    case "task_completed":
      return "text-blue-500";
    case "task_deleted":
      return "text-gray-500";
    case "deadline_approaching":
      return "text-yellow-500";
    case "deadline_passed":
      return "text-red-500";
    case "system":
    default:
      return "text-indigo-500";
  }
}

// Helper function to format notification time
// Uses shared date-utils for consistent timezone handling
export function formatNotificationTime(dateString: string): string {
  return formatRelativeTime(dateString);
}
