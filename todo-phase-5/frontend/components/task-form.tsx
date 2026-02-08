"use client";

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiPost } from "@/lib/api";
import { useToast } from "@/components/ui/toast";
import { Button } from "@/components/ui/button";
import type { Task, TaskCreate } from "@/types/task";

export function TaskForm() {
  const queryClient = useQueryClient();
  const toast = useToast();
  const [title, setTitle] = useState("");
  const [error, setError] = useState("");

  const createMutation = useMutation({
    mutationFn: (data: TaskCreate) => apiPost<Task>("/api/tasks", data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      setTitle("");
      setError("");
      toast.success("Task created!", "Your new task has been added to the list");
    },
    onError: () => {
      setError("Failed to create task. Please try again.");
      toast.error("Failed to create task", "Please try again");
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    const trimmed = title.trim();
    if (!trimmed) {
      setError("Please enter a task title");
      return;
    }

    if (trimmed.length > 500) {
      setError("Title must be 500 characters or less");
      return;
    }

    createMutation.mutate({ title: trimmed });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="relative">
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="What needs to be done?"
          className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-3 text-sm placeholder-gray-400 dark:placeholder-gray-500 dark:text-white shadow-sm transition-all focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
          disabled={createMutation.isPending}
        />
        {title.length > 0 && (
          <span className={`absolute right-3 top-1/2 -translate-y-1/2 text-xs ${title.length > 450 ? "text-yellow-500" : "text-gray-400 dark:text-gray-500"}`}>
            {title.length}/500
          </span>
        )}
      </div>
      <Button
        type="submit"
        className="w-full"
        isLoading={createMutation.isPending}
        disabled={!title.trim()}
      >
        <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
        Add Task
      </Button>
      {error && (
        <div className="flex items-center gap-2 rounded-lg bg-red-50 dark:bg-red-900/30 px-3 py-2 text-sm text-red-600 dark:text-red-400">
          <svg className="h-4 w-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {error}
        </div>
      )}
    </form>
  );
}
