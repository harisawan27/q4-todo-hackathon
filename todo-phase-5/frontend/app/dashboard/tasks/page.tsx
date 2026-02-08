"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api";
import type { Task, Priority } from "@/types/task";
import { TaskItem } from "@/components/task-item";
import { TaskFormDialog } from "@/components/task-form-dialog";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";

type FilterStatus = "all" | "active" | "completed";
type SortBy = "created" | "updated" | "title" | "priority" | "due_date";

const PRIORITY_ORDER: Record<Priority, number> = {
  urgent: 0,
  high: 1,
  medium: 2,
  low: 3,
};

// Helper to get priority order with null handling (null goes last)
const getPriorityOrder = (priority: Priority | null): number => {
  if (priority === null) return 4;
  return PRIORITY_ORDER[priority];
};

export default function TasksPage() {
  const [filter, setFilter] = useState<FilterStatus>("all");
  const [sortBy, setSortBy] = useState<SortBy>("created");
  const [searchQuery, setSearchQuery] = useState("");
  const [showCreateDialog, setShowCreateDialog] = useState(false);

  const {
    data: tasks,
    isLoading,
    error,
  } = useQuery<Task[]>({
    queryKey: ["tasks"],
    queryFn: () => apiGet<Task[]>("/api/tasks"),
  });

  // Filter and sort tasks
  const filteredTasks = tasks
    ?.filter((task) => {
      // Status filter
      if (filter === "active" && task.completed) return false;
      if (filter === "completed" && !task.completed) return false;

      // Search filter (search in title, description, and tags)
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
        case "updated":
          return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime();
        case "priority":
          return getPriorityOrder(a.priority) - getPriorityOrder(b.priority);
        case "due_date":
          // Tasks without due date go to the end
          if (!a.due_date && !b.due_date) return 0;
          if (!a.due_date) return 1;
          if (!b.due_date) return -1;
          return new Date(a.due_date).getTime() - new Date(b.due_date).getTime();
        case "created":
        default:
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      }
    });

  const totalTasks = tasks?.length || 0;
  const completedCount = tasks?.filter((t) => t.completed).length || 0;
  const activeCount = totalTasks - completedCount;
  const overdueCount = tasks?.filter((t) => {
    if (!t.due_date || t.completed) return false;
    return new Date(t.due_date) < new Date(new Date().toDateString());
  }).length || 0;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">All Tasks</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Manage and organize all your tasks in one place
          </p>
        </div>
        <div className="flex items-center gap-2 text-sm flex-wrap">
          <span className="inline-flex items-center gap-1.5 rounded-full bg-blue-100 dark:bg-blue-900/30 px-3 py-1 text-blue-700 dark:text-blue-300">
            <span className="h-2 w-2 rounded-full bg-blue-500" />
            {totalTasks} total
          </span>
          <span className="inline-flex items-center gap-1.5 rounded-full bg-yellow-100 dark:bg-yellow-900/30 px-3 py-1 text-yellow-700 dark:text-yellow-300">
            {activeCount} active
          </span>
          <span className="inline-flex items-center gap-1.5 rounded-full bg-green-100 dark:bg-green-900/30 px-3 py-1 text-green-700 dark:text-green-300">
            {completedCount} done
          </span>
          {overdueCount > 0 && (
            <span className="inline-flex items-center gap-1.5 rounded-full bg-red-100 dark:bg-red-900/30 px-3 py-1 text-red-700 dark:text-red-300">
              {overdueCount} overdue
            </span>
          )}
        </div>
      </div>

      {/* Add Task Button */}
      <Card>
        <CardContent className="py-6">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 p-3">
                <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
              </div>
              <div>
                <h2 className="font-semibold text-gray-900 dark:text-white">Create New Task</h2>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Add a task with description, due date, priority, and tags
                </p>
              </div>
            </div>
            <Button onClick={() => setShowCreateDialog(true)} className="w-full sm:w-auto">
              <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Add Task
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Filters and Search */}
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

            <div className="flex items-center gap-3 flex-wrap">
              {/* Filter Buttons */}
              <div className="flex rounded-lg border border-gray-200 dark:border-gray-600 p-1">
                {(["all", "active", "completed"] as const).map((status) => (
                  <button
                    key={status}
                    onClick={() => setFilter(status)}
                    className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
                      filter === status
                        ? "bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300"
                        : "text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700"
                    }`}
                  >
                    {status.charAt(0).toUpperCase() + status.slice(1)}
                  </button>
                ))}
              </div>

              {/* Sort Dropdown */}
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as SortBy)}
                className="rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:text-white"
              >
                <option value="created">Newest First</option>
                <option value="updated">Recently Updated</option>
                <option value="title">Alphabetical</option>
                <option value="priority">Priority</option>
                <option value="due_date">Due Date</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Task List */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="rounded-lg bg-purple-100 dark:bg-purple-900/30 p-2">
                <svg className="h-5 w-5 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
              </div>
              <div>
                <h2 className="font-semibold text-gray-900 dark:text-white">Task List</h2>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {filteredTasks?.length || 0} task{(filteredTasks?.length || 0) !== 1 ? "s" : ""} showing
                </p>
              </div>
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
          ) : !filteredTasks || filteredTasks.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 px-6 text-center">
              <div className="relative">
                <div className="absolute -inset-4 rounded-full bg-blue-100/50 dark:bg-blue-900/20 blur-xl" />
                <div className="relative rounded-2xl bg-gradient-to-br from-blue-100 to-indigo-100 dark:from-blue-900/50 dark:to-indigo-900/50 p-6">
                  <svg className="h-12 w-12 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                  </svg>
                </div>
              </div>
              <h3 className="mt-6 text-lg font-semibold text-gray-900 dark:text-white">
                {searchQuery ? "No matching tasks" : filter !== "all" ? `No ${filter} tasks` : "No tasks yet"}
              </h3>
              <p className="mt-2 max-w-xs text-sm text-gray-500 dark:text-gray-400">
                {searchQuery
                  ? "Try adjusting your search query"
                  : filter !== "all"
                  ? `You don't have any ${filter} tasks at the moment`
                  : "Get started by creating your first task"}
              </p>
              {!searchQuery && filter === "all" && (
                <Button onClick={() => setShowCreateDialog(true)} className="mt-4">
                  <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  Create Your First Task
                </Button>
              )}
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

      {/* Create Task Dialog */}
      <TaskFormDialog isOpen={showCreateDialog} onClose={() => setShowCreateDialog(false)} />
    </div>
  );
}
