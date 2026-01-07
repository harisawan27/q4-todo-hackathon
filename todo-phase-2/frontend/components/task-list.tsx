"use client";

import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api";
import type { Task } from "@/types/task";
import { TaskItem } from "./task-item";
import { EmptyState } from "./empty-state";

export function TaskList() {
  const {
    data: tasks,
    isLoading,
    error,
  } = useQuery<Task[]>({
    queryKey: ["tasks"],
    queryFn: () => apiGet<Task[]>("/api/tasks"),
  });

  // Sort tasks: incomplete first (by priority), then completed
  const sortedTasks = tasks?.slice().sort((a, b) => {
    // Completed tasks go to the bottom
    if (a.completed !== b.completed) {
      return a.completed ? 1 : -1;
    }
    // Within same completion status, sort by created_at (newest first)
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
  });

  if (isLoading) {
    return (
      <div className="space-y-3 p-4">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="flex items-center gap-4 px-5 py-4 rounded-xl border border-gray-100 dark:border-gray-700">
            <div className="h-6 w-6 rounded-full skeleton" />
            <div className="flex-1 space-y-2">
              <div className="h-4 w-3/4 rounded skeleton" />
              <div className="h-3 w-1/4 rounded skeleton" />
            </div>
            <div className="h-6 w-20 rounded-full skeleton" />
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-12 px-6">
        <div className="rounded-full bg-red-100 dark:bg-red-900/30 p-3 mb-4">
          <svg className="h-6 w-6 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <p className="text-sm font-medium text-gray-900 dark:text-white">Failed to load tasks</p>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Please try refreshing the page</p>
      </div>
    );
  }

  if (!sortedTasks || sortedTasks.length === 0) {
    return <EmptyState />;
  }

  return (
    <ul className="space-y-3 p-4 stagger-children">
      {sortedTasks.map((task) => (
        <TaskItem key={task.id} task={task} />
      ))}
    </ul>
  );
}
