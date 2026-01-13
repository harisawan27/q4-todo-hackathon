"use client";

import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api";
import type { Task, Priority } from "@/types/task";
import { Card, CardContent, CardHeader } from "@/components/ui/card";

const PRIORITY_COLORS: Record<Priority, { bg: string; text: string; bar: string }> = {
  urgent: { bg: "bg-red-100 dark:bg-red-900/30", text: "text-red-700 dark:text-red-300", bar: "bg-red-500" },
  high: { bg: "bg-orange-100 dark:bg-orange-900/30", text: "text-orange-700 dark:text-orange-300", bar: "bg-orange-500" },
  medium: { bg: "bg-yellow-100 dark:bg-yellow-900/30", text: "text-yellow-700 dark:text-yellow-300", bar: "bg-yellow-500" },
  low: { bg: "bg-green-100 dark:bg-green-900/30", text: "text-green-700 dark:text-green-300", bar: "bg-green-500" },
};

export default function StatsPage() {
  const {
    data: tasks,
    isLoading,
    error,
  } = useQuery<Task[]>({
    queryKey: ["tasks"],
    queryFn: () => apiGet<Task[]>("/api/tasks"),
  });

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Statistics</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Loading your task analytics...</p>
        </div>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <Card key={i}>
              <CardContent className="py-6">
                <div className="h-16 skeleton rounded" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-16 px-6">
        <div className="rounded-full bg-red-100 dark:bg-red-900/30 p-3 mb-4">
          <svg className="h-6 w-6 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <p className="text-sm font-medium text-gray-900 dark:text-white">Failed to load statistics</p>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Please try refreshing the page</p>
      </div>
    );
  }

  const allTasks = tasks || [];
  const totalTasks = allTasks.length;
  const completedTasks = allTasks.filter((t) => t.completed);
  const activeTasks = allTasks.filter((t) => !t.completed);
  const completedCount = completedTasks.length;
  const activeCount = activeTasks.length;
  const completionRate = totalTasks > 0 ? Math.round((completedCount / totalTasks) * 100) : 0;

  // Due date statistics
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const tomorrow = new Date(today);
  tomorrow.setDate(tomorrow.getDate() + 1);
  const weekFromNow = new Date(today);
  weekFromNow.setDate(weekFromNow.getDate() + 7);

  const overdueCount = activeTasks.filter((t) => {
    if (!t.due_date) return false;
    return new Date(t.due_date) < today;
  }).length;

  const dueTodayCount = activeTasks.filter((t) => {
    if (!t.due_date) return false;
    const dueDate = new Date(t.due_date);
    return dueDate >= today && dueDate < tomorrow;
  }).length;

  const dueThisWeekCount = activeTasks.filter((t) => {
    if (!t.due_date) return false;
    const dueDate = new Date(t.due_date);
    return dueDate >= today && dueDate < weekFromNow;
  }).length;

  const noDueDateCount = activeTasks.filter((t) => !t.due_date).length;

  // Priority statistics
  const priorityStats: Record<Priority, { total: number; completed: number }> = {
    urgent: { total: 0, completed: 0 },
    high: { total: 0, completed: 0 },
    medium: { total: 0, completed: 0 },
    low: { total: 0, completed: 0 },
  };

  allTasks.forEach((task) => {
    if (task.priority) {
      priorityStats[task.priority].total++;
      if (task.completed) {
        priorityStats[task.priority].completed++;
      }
    }
  });

  const noPriorityCount = allTasks.filter((t) => !t.priority).length;

  // Tag statistics
  const tagCounts: Record<string, { total: number; completed: number }> = {};
  allTasks.forEach((task) => {
    task.tags.forEach((tag) => {
      if (!tagCounts[tag]) {
        tagCounts[tag] = { total: 0, completed: 0 };
      }
      tagCounts[tag].total++;
      if (task.completed) {
        tagCounts[tag].completed++;
      }
    });
  });

  const topTags = Object.entries(tagCounts)
    .sort((a, b) => b[1].total - a[1].total)
    .slice(0, 6);

  // Weekly completion statistics
  const weekAgo = new Date();
  weekAgo.setDate(weekAgo.getDate() - 7);
  const completedThisWeek = completedTasks.filter(
    (t) => new Date(t.updated_at) > weekAgo
  ).length;

  const twoWeeksAgo = new Date();
  twoWeeksAgo.setDate(twoWeeksAgo.getDate() - 14);
  const completedLastWeek = completedTasks.filter((t) => {
    const date = new Date(t.updated_at);
    return date > twoWeeksAgo && date <= weekAgo;
  }).length;

  const weeklyChange = completedLastWeek > 0
    ? Math.round(((completedThisWeek - completedLastWeek) / completedLastWeek) * 100)
    : completedThisWeek > 0 ? 100 : 0;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Statistics</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          Track your productivity and task management insights
        </p>
      </div>

      {/* Main Stats */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="py-4">
            <div className="flex items-center gap-4">
              <div className="rounded-xl bg-blue-100 dark:bg-blue-900/30 p-3">
                <svg className="h-6 w-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{totalTasks}</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">Total Tasks</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="py-4">
            <div className="flex items-center gap-4">
              <div className="rounded-xl bg-green-100 dark:bg-green-900/30 p-3">
                <svg className="h-6 w-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{completedCount}</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">Completed</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="py-4">
            <div className="flex items-center gap-4">
              <div className="rounded-xl bg-yellow-100 dark:bg-yellow-900/30 p-3">
                <svg className="h-6 w-6 text-yellow-600 dark:text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{activeCount}</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">In Progress</p>
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
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{completionRate}%</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">Completion Rate</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Due Date Overview */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <div className="rounded-lg bg-blue-100 dark:bg-blue-900/30 p-2">
                <svg className="h-5 w-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <h2 className="font-semibold text-gray-900 dark:text-white">Due Date Overview</h2>
                <p className="text-xs text-gray-500 dark:text-gray-400">Active tasks by due date</p>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 rounded-full bg-red-500" />
                  <span className="text-sm text-gray-600 dark:text-gray-400">Overdue</span>
                </div>
                <span className="text-sm font-semibold text-gray-900 dark:text-white">{overdueCount}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 rounded-full bg-orange-500" />
                  <span className="text-sm text-gray-600 dark:text-gray-400">Due Today</span>
                </div>
                <span className="text-sm font-semibold text-gray-900 dark:text-white">{dueTodayCount}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 rounded-full bg-blue-500" />
                  <span className="text-sm text-gray-600 dark:text-gray-400">Due This Week</span>
                </div>
                <span className="text-sm font-semibold text-gray-900 dark:text-white">{dueThisWeekCount}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 rounded-full bg-gray-400" />
                  <span className="text-sm text-gray-600 dark:text-gray-400">No Due Date</span>
                </div>
                <span className="text-sm font-semibold text-gray-900 dark:text-white">{noDueDateCount}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Priority Breakdown */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <div className="rounded-lg bg-orange-100 dark:bg-orange-900/30 p-2">
                <svg className="h-5 w-5 text-orange-600 dark:text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12" />
                </svg>
              </div>
              <div>
                <h2 className="font-semibold text-gray-900 dark:text-white">Priority Breakdown</h2>
                <p className="text-xs text-gray-500 dark:text-gray-400">Tasks by priority level</p>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {(["urgent", "high", "medium", "low"] as Priority[]).map((priority) => {
                const stats = priorityStats[priority];
                const percentage = stats.total > 0 ? Math.round((stats.completed / stats.total) * 100) : 0;
                return (
                  <div key={priority} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className={`text-sm font-medium capitalize ${PRIORITY_COLORS[priority].text}`}>
                        {priority}
                      </span>
                      <span className="text-sm text-gray-500 dark:text-gray-400">
                        {stats.completed}/{stats.total} ({percentage}%)
                      </span>
                    </div>
                    <div className="h-2 rounded-full bg-gray-200 dark:bg-gray-700 overflow-hidden">
                      <div
                        className={`h-full rounded-full ${PRIORITY_COLORS[priority].bar} transition-all duration-300`}
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                );
              })}
              {noPriorityCount > 0 && (
                <div className="pt-2 border-t border-gray-200 dark:border-gray-700">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500 dark:text-gray-400">No Priority Set</span>
                    <span className="font-medium text-gray-900 dark:text-white">{noPriorityCount} tasks</span>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Weekly Progress */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <div className="rounded-lg bg-green-100 dark:bg-green-900/30 p-2">
                <svg className="h-5 w-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div>
                <h2 className="font-semibold text-gray-900 dark:text-white">Weekly Progress</h2>
                <p className="text-xs text-gray-500 dark:text-gray-400">Tasks completed over time</p>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-3xl font-bold text-gray-900 dark:text-white">{completedThisWeek}</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Completed this week</p>
                </div>
                <div className={`flex items-center gap-1 px-2.5 py-1 rounded-full text-sm font-medium ${
                  weeklyChange >= 0
                    ? "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300"
                    : "bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300"
                }`}>
                  <svg className={`h-4 w-4 ${weeklyChange < 0 ? "rotate-180" : ""}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
                  </svg>
                  {Math.abs(weeklyChange)}%
                </div>
              </div>
              <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500 dark:text-gray-400">Last week</span>
                  <span className="font-medium text-gray-900 dark:text-white">{completedLastWeek} tasks</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Top Tags */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <div className="rounded-lg bg-indigo-100 dark:bg-indigo-900/30 p-2">
                <svg className="h-5 w-5 text-indigo-600 dark:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                </svg>
              </div>
              <div>
                <h2 className="font-semibold text-gray-900 dark:text-white">Top Tags</h2>
                <p className="text-xs text-gray-500 dark:text-gray-400">Most used task categories</p>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {topTags.length === 0 ? (
              <div className="text-center py-6">
                <p className="text-sm text-gray-500 dark:text-gray-400">No tags used yet</p>
                <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                  Add tags to your tasks to see them here
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {topTags.map(([tag, stats]) => {
                  const percentage = stats.total > 0 ? Math.round((stats.completed / stats.total) * 100) : 0;
                  return (
                    <div key={tag} className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="inline-flex items-center rounded-full bg-gray-100 dark:bg-gray-700 px-2.5 py-0.5 text-xs font-medium text-gray-800 dark:text-gray-200">
                          #{tag}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-gray-500 dark:text-gray-400">
                          {stats.completed}/{stats.total}
                        </span>
                        <div className="w-16 h-2 rounded-full bg-gray-200 dark:bg-gray-700 overflow-hidden">
                          <div
                            className="h-full rounded-full bg-indigo-500 transition-all duration-300"
                            style={{ width: `${percentage}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Empty State for No Tasks */}
      {totalTasks === 0 && (
        <Card>
          <CardContent className="py-16">
            <div className="flex flex-col items-center justify-center text-center">
              <div className="relative">
                <div className="absolute -inset-4 rounded-full bg-purple-100/50 dark:bg-purple-900/20 blur-xl" />
                <div className="relative rounded-2xl bg-gradient-to-br from-purple-100 to-indigo-100 dark:from-purple-900/50 dark:to-indigo-900/50 p-6">
                  <svg className="h-12 w-12 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
              </div>
              <h3 className="mt-6 text-lg font-semibold text-gray-900 dark:text-white">No statistics yet</h3>
              <p className="mt-2 max-w-sm text-sm text-gray-500 dark:text-gray-400">
                Create some tasks to start tracking your productivity and see insights here.
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
