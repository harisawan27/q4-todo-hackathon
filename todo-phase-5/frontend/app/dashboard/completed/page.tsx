"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiGet, apiDelete } from "@/lib/api";
import type { Task } from "@/types/task";
import { TaskItem } from "@/components/task-item";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import { useToast } from "@/components/ui/toast";

type SortBy = "completed" | "created" | "title";

export default function CompletedPage() {
  const [sortBy, setSortBy] = useState<SortBy>("completed");
  const [searchQuery, setSearchQuery] = useState("");
  const [showClearDialog, setShowClearDialog] = useState(false);
  const queryClient = useQueryClient();
  const toast = useToast();

  const {
    data: tasks,
    isLoading,
    error,
  } = useQuery<Task[]>({
    queryKey: ["tasks"],
    queryFn: () => apiGet<Task[]>("/api/tasks"),
  });

  const completedTasks = tasks?.filter((task) => task.completed) || [];

  // Filter and sort completed tasks
  const filteredTasks = completedTasks
    .filter((task) => {
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        const matchesTitle = task.title.toLowerCase().includes(query);
        const matchesDescription = task.description?.toLowerCase().includes(query);
        const matchesTags = task.tags.some((tag) => tag.toLowerCase().includes(query));
        if (!matchesTitle && !matchesDescription && !matchesTags) return false;
      }
      return true;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case "title":
          return a.title.localeCompare(b.title);
        case "created":
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
        case "completed":
        default:
          return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime();
      }
    });

  const clearCompletedMutation = useMutation({
    mutationFn: async () => {
      // Delete all completed tasks
      await Promise.all(completedTasks.map((task) => apiDelete(`/api/tasks/${task.id}`)));
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      toast.success("Completed tasks cleared", "All completed tasks have been removed");
      setShowClearDialog(false);
    },
    onError: () => {
      toast.error("Failed to clear tasks", "Please try again");
    },
  });

  const totalCompleted = completedTasks.length;
  const thisWeekCount = completedTasks.filter((task) => {
    const weekAgo = new Date();
    weekAgo.setDate(weekAgo.getDate() - 7);
    return new Date(task.updated_at) > weekAgo;
  }).length;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Completed Tasks</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Review and manage your completed tasks
          </p>
        </div>
        <div className="flex items-center gap-2 text-sm">
          <span className="inline-flex items-center gap-1.5 rounded-full bg-green-100 dark:bg-green-900/30 px-3 py-1 text-green-700 dark:text-green-300">
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            {totalCompleted} completed
          </span>
          <span className="inline-flex items-center gap-1.5 rounded-full bg-blue-100 dark:bg-blue-900/30 px-3 py-1 text-blue-700 dark:text-blue-300">
            {thisWeekCount} this week
          </span>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <Card>
          <CardContent className="py-4">
            <div className="flex items-center gap-4">
              <div className="rounded-xl bg-green-100 dark:bg-green-900/30 p-3">
                <svg className="h-6 w-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{totalCompleted}</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">Total Completed</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="py-4">
            <div className="flex items-center gap-4">
              <div className="rounded-xl bg-blue-100 dark:bg-blue-900/30 p-3">
                <svg className="h-6 w-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{thisWeekCount}</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">This Week</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="py-4">
            <div className="flex items-center gap-4">
              <div className="rounded-xl bg-purple-100 dark:bg-purple-900/30 p-3">
                <svg className="h-6 w-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {tasks && tasks.length > 0
                    ? Math.round((completedTasks.length / tasks.length) * 100)
                    : 0}%
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-400">Completion Rate</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Actions */}
      <Card>
        <CardContent className="py-4">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            {/* Search */}
            <div className="relative flex-1 max-w-md">
              <svg
                className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                type="text"
                placeholder="Search by title, description, or tags..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 pl-10 pr-4 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:text-white dark:placeholder-gray-400"
              />
            </div>

            <div className="flex items-center gap-3">
              {/* Sort Dropdown */}
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as SortBy)}
                className="rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:text-white"
              >
                <option value="completed">Recently Completed</option>
                <option value="created">Date Created</option>
                <option value="title">Alphabetical</option>
              </select>

              {/* Clear All Button */}
              {totalCompleted > 0 && (
                <Button
                  variant="outline"
                  onClick={() => setShowClearDialog(true)}
                  className="text-red-600 border-red-200 hover:bg-red-50 dark:border-red-800 dark:hover:bg-red-900/20"
                >
                  <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                  Clear All
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Task List */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <div className="rounded-lg bg-green-100 dark:bg-green-900/30 p-2">
              <svg className="h-5 w-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <h2 className="font-semibold text-gray-900 dark:text-white">Completed Tasks</h2>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {filteredTasks.length} task{filteredTasks.length !== 1 ? "s" : ""} completed
              </p>
            </div>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="space-y-3 p-4">
              {[...Array(5)].map((_, i) => (
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
          ) : error ? (
            <div className="flex flex-col items-center justify-center py-12 px-6">
              <div className="rounded-full bg-red-100 dark:bg-red-900/30 p-3 mb-4">
                <svg className="h-6 w-6 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <p className="text-sm font-medium text-gray-900 dark:text-white">Failed to load tasks</p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Please try refreshing the page</p>
            </div>
          ) : filteredTasks.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 px-6 text-center">
              <div className="relative">
                <div className="absolute -inset-4 rounded-full bg-green-100/50 dark:bg-green-900/20 blur-xl" />
                <div className="relative rounded-2xl bg-gradient-to-br from-green-100 to-emerald-100 dark:from-green-900/50 dark:to-emerald-900/50 p-6">
                  <svg className="h-12 w-12 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
              <h3 className="mt-6 text-lg font-semibold text-gray-900 dark:text-white">
                {searchQuery ? "No matching completed tasks" : "No completed tasks yet"}
              </h3>
              <p className="mt-2 max-w-xs text-sm text-gray-500 dark:text-gray-400">
                {searchQuery
                  ? "Try adjusting your search query"
                  : "Complete some tasks to see them here. You've got this!"}
              </p>
            </div>
          ) : (
            <ul className="space-y-3 p-4 stagger-children">
              {filteredTasks.map((task) => (
                <TaskItem key={task.id} task={task} />
              ))}
            </ul>
          )}
        </CardContent>
      </Card>

      {/* Clear Confirmation Dialog */}
      <ConfirmDialog
        isOpen={showClearDialog}
        onClose={() => setShowClearDialog(false)}
        onConfirm={() => clearCompletedMutation.mutate()}
        title="Clear Completed Tasks"
        message={`Are you sure you want to delete all ${totalCompleted} completed task${totalCompleted !== 1 ? "s" : ""}? This action cannot be undone.`}
        confirmText="Clear All"
        cancelText="Cancel"
        variant="danger"
        isLoading={clearCompletedMutation.isPending}
      />
    </div>
  );
}
