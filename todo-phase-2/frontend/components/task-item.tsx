"use client";

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiPost, apiDelete } from "@/lib/api";
import { useToast } from "@/components/ui/toast";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import { TaskFormDialog } from "@/components/task-form-dialog";
import type { Task } from "@/types/task";
import { PRIORITY_CONFIG } from "@/types/task";
import {
  getDueDateStatus,
  formatDueDateTime,
  getHoursRemaining,
  formatCreatedAt,
} from "@/lib/date-utils";

interface TaskItemProps {
  task: Task;
}

export function TaskItem({ task }: TaskItemProps) {
  const queryClient = useQueryClient();
  const toast = useToast();
  const [isExpanded, setIsExpanded] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);

  const toggleMutation = useMutation({
    mutationFn: () => apiPost<Task>(`/api/tasks/${task.id}/toggle`),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      toast.success(
        data.completed ? "Task completed!" : "Task reopened",
        data.completed ? "Great job on finishing this task!" : "Task moved back to in progress"
      );
    },
    onError: () => {
      toast.error("Failed to update task", "Please try again");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => apiDelete(`/api/tasks/${task.id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      toast.success("Task deleted", "The task has been permanently removed");
    },
    onError: () => {
      toast.error("Failed to delete task", "Please try again");
    },
  });

  const handleToggle = () => {
    toggleMutation.mutate();
  };

  const confirmDelete = () => {
    deleteMutation.mutate();
    setShowDeleteDialog(false);
  };

  const dueDateStatus = getDueDateStatus(task.due_date, task.due_time);
  const priorityConfig = task.priority ? PRIORITY_CONFIG[task.priority] : null;
  const hasDetails = task.description || task.tags.length > 0;
  const hoursRemaining = getHoursRemaining(task.due_date, task.due_time);

  return (
    <>
      <li className="group bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 shadow-sm hover:shadow-md transition-all">
        {/* Main row */}
        <div className="flex items-start gap-4 px-5 py-4">
          {/* Checkbox */}
          <button
            onClick={handleToggle}
            disabled={toggleMutation.isPending}
            className={`mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full border-2 transition-all duration-200 ${
              task.completed
                ? "border-green-500 bg-green-500 text-white"
                : "border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 hover:border-green-400 hover:bg-green-50 dark:hover:bg-green-900/30"
            } ${toggleMutation.isPending ? "opacity-50" : ""}`}
            aria-label={task.completed ? "Mark as incomplete" : "Mark as complete"}
          >
            {task.completed && (
              <svg className="h-3.5 w-3.5 animate-check" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                  clipRule="evenodd"
                />
              </svg>
            )}
          </button>

          {/* Task content */}
          <div className="flex-1 min-w-0">
            {/* Title row */}
            <div className="flex items-start gap-2">
              <p
                className={`text-sm font-medium transition-all flex-1 ${
                  task.completed ? "text-gray-400 dark:text-gray-500 line-through" : "text-gray-900 dark:text-white"
                }`}
              >
                {task.title}
              </p>

              {/* Priority badge - only show if priority is set */}
              {priorityConfig && (
                <span
                  className={`shrink-0 inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${
                    task.priority === "urgent"
                      ? "bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300"
                      : task.priority === "high"
                      ? "bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300"
                      : task.priority === "medium"
                      ? "bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300"
                      : "bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400"
                  }`}
                >
                  <span>{priorityConfig.icon}</span>
                  <span className="hidden sm:inline">{priorityConfig.label}</span>
                </span>
              )}
            </div>

            {/* Urgency indicator - hours remaining */}
            {hoursRemaining !== null && !task.completed && (
              <div className="flex items-center gap-1.5 mt-2">
                <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-gradient-to-r from-red-50 to-orange-50 dark:from-red-900/20 dark:to-orange-900/20 border border-red-200 dark:border-red-800">
                  <svg className="h-3.5 w-3.5 text-red-600 dark:text-red-400 animate-pulse" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                  </svg>
                  <span className="text-xs font-semibold text-red-700 dark:text-red-300">
                    {hoursRemaining === 0 ? (
                      "Less than 1 hour left!"
                    ) : hoursRemaining === 1 ? (
                      "1 hour left!"
                    ) : (
                      `${hoursRemaining} hours left!`
                    )}
                  </span>
                </div>
              </div>
            )}

            {/* Meta row */}
            <div className="flex flex-wrap items-center gap-3 mt-1.5 text-xs">
              {/* Due date */}
              {task.due_date && (
                <span
                  className={`inline-flex items-center gap-1 ${
                    task.completed
                      ? "text-gray-400 dark:text-gray-500"
                      : dueDateStatus === "overdue"
                      ? "text-red-600 dark:text-red-400"
                      : dueDateStatus === "today"
                      ? "text-orange-600 dark:text-orange-400"
                      : "text-gray-500 dark:text-gray-400"
                  }`}
                >
                  <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  <span className="font-medium">
                    {dueDateStatus === "overdue" && !task.completed && "Overdue: "}
                    {formatDueDateTime(task.due_date, task.due_time)}
                  </span>
                </span>
              )}

              {/* Created date */}
              <span className="text-gray-400 dark:text-gray-500">
                Created {formatCreatedAt(task.created_at)}
              </span>

              {/* Expand button if has details */}
              {hasDetails && (
                <button
                  onClick={() => setIsExpanded(!isExpanded)}
                  className="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium"
                >
                  {isExpanded ? "Show less" : "Show more"}
                </button>
              )}
            </div>

            {/* Expanded content */}
            {isExpanded && hasDetails && (
              <div className="mt-3 space-y-2">
                {/* Description */}
                {task.description && (
                  <p className="text-sm text-gray-600 dark:text-gray-300 whitespace-pre-wrap">
                    {task.description}
                  </p>
                )}

                {/* Tags */}
                {task.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1.5">
                    {task.tags.map((tag) => (
                      <span
                        key={tag}
                        className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300"
                      >
                        #{tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Status badge */}
          <span
            className={`hidden shrink-0 rounded-full px-2.5 py-0.5 text-xs font-medium sm:inline-flex ${
              task.completed
                ? "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300"
                : "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300"
            }`}
          >
            {task.completed ? "Completed" : "In Progress"}
          </span>

          {/* Actions */}
          <div className="flex shrink-0 items-center gap-1 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity">
            <button
              onClick={() => setShowEditDialog(true)}
              className="rounded-lg p-2 text-gray-400 hover:bg-blue-50 dark:hover:bg-blue-900/30 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
              aria-label="Edit task"
            >
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                />
              </svg>
            </button>
            <button
              onClick={() => setShowDeleteDialog(true)}
              disabled={deleteMutation.isPending}
              className="rounded-lg p-2 text-gray-400 hover:bg-red-50 dark:hover:bg-red-900/30 hover:text-red-600 dark:hover:text-red-400 transition-colors"
              aria-label="Delete task"
            >
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
            </button>
          </div>
        </div>
      </li>

      {/* Edit Dialog */}
      <TaskFormDialog
        isOpen={showEditDialog}
        onClose={() => setShowEditDialog(false)}
        task={task}
      />

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        isOpen={showDeleteDialog}
        onClose={() => setShowDeleteDialog(false)}
        onConfirm={confirmDelete}
        title="Delete Task"
        message={`Are you sure you want to delete "${task.title}"? This action cannot be undone.`}
        confirmText="Delete Task"
        cancelText="Keep Task"
        variant="danger"
        isLoading={deleteMutation.isPending}
      />
    </>
  );
}
