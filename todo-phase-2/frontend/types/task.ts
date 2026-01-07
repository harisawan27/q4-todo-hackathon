/**
 * Task TypeScript types matching OpenAPI contract schemas
 */

export type Priority = "low" | "medium" | "high" | "urgent";

export interface Task {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  due_date: string | null;  // ISO date string (YYYY-MM-DD)
  priority: Priority | null;
  tags: string[];
  completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string | null;
  due_date?: string | null;
  priority?: Priority;
  tags?: string[];
}

export interface TaskUpdate {
  title?: string;
  description?: string | null;
  due_date?: string | null;
  priority?: Priority;
  tags?: string[];
  completed?: boolean;
}

export interface ApiError {
  detail: string;
  code: string;
  status: number;
}

// Priority display helpers
export const PRIORITY_CONFIG = {
  low: { label: "Low", color: "gray", icon: "↓" },
  medium: { label: "Medium", color: "blue", icon: "→" },
  high: { label: "High", color: "orange", icon: "↑" },
  urgent: { label: "Urgent", color: "red", icon: "⚡" },
} as const;
