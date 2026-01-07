"use client";

import { useState } from "react";
import { StatsCards } from "@/components/stats-cards";
import { TaskList } from "@/components/task-list";
import { TaskFormDialog } from "@/components/task-form-dialog";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";

export default function DashboardPage() {
  const [showCreateDialog, setShowCreateDialog] = useState(false);

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Track and manage your tasks efficiently</p>
        </div>
        <div className="hidden sm:block">
          <span className="inline-flex items-center gap-2 rounded-full bg-green-50 dark:bg-green-900/30 px-3 py-1 text-sm text-green-700 dark:text-green-300">
            <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
            All systems operational
          </span>
        </div>
      </div>

      {/* Stats */}
      <StatsCards />

      {/* Main Content */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Create Task Card */}
        <Card className="lg:col-span-1">
          <CardContent className="py-8">
            <div className="flex flex-col items-center text-center">
              <div className="rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 p-4 mb-4">
                <svg className="h-8 w-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
              </div>
              <h2 className="font-semibold text-gray-900 dark:text-white mb-1">Create New Task</h2>
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                Add a task with details, due date, priority, and tags
              </p>
              <Button onClick={() => setShowCreateDialog(true)} className="w-full">
                <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Add Task
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Task List */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="rounded-lg bg-purple-100 dark:bg-purple-900/30 p-2">
                  <svg className="h-5 w-5 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                  </svg>
                </div>
                <div>
                  <h2 className="font-semibold text-gray-900 dark:text-white">Your Tasks</h2>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Manage and track your progress</p>
                </div>
              </div>
              <a href="/dashboard/tasks" className="rounded-lg px-3 py-1.5 text-sm font-medium text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
                View All
              </a>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <TaskList />
          </CardContent>
        </Card>
      </div>

      {/* Create Task Dialog */}
      <TaskFormDialog isOpen={showCreateDialog} onClose={() => setShowCreateDialog(false)} />
    </div>
  );
}
