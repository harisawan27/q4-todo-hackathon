"use client";

import { useState, useEffect } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/toast";
import { apiPost, apiPatch } from "@/lib/api";
import type { Task, TaskCreate, TaskUpdate, Priority } from "@/types/task";
import { PRIORITY_CONFIG } from "@/types/task";

interface TaskFormDialogProps {
  isOpen: boolean;
  onClose: () => void;
  task?: Task; // If provided, we're editing; otherwise creating
}

const PRIORITY_OPTIONS: Priority[] = ["low", "medium", "high", "urgent"];

export function TaskFormDialog({ isOpen, onClose, task }: TaskFormDialogProps) {
  const queryClient = useQueryClient();
  const toast = useToast();
  const isEditing = !!task;

  // Form state
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [dueDate, setDueDate] = useState("");
  const [priority, setPriority] = useState<Priority | null>(null);
  const [tagInput, setTagInput] = useState("");
  const [tags, setTags] = useState<string[]>([]);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Reset form when dialog opens/closes or task changes
  useEffect(() => {
    if (isOpen) {
      if (task) {
        setTitle(task.title);
        setDescription(task.description || "");
        setDueDate(task.due_date || "");
        setPriority(task.priority);
        setTags(task.tags || []);
      } else {
        setTitle("");
        setDescription("");
        setDueDate("");
        setPriority(null);
        setTags([]);
      }
      setTagInput("");
      setErrors({});
    }
  }, [isOpen, task]);

  // Create mutation
  const createMutation = useMutation({
    mutationFn: (data: TaskCreate) => apiPost<Task>("/api/tasks", data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      toast.success("Task created!", "Your new task has been added");
      onClose();
    },
    onError: () => {
      toast.error("Failed to create task", "Please try again");
    },
  });

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: (data: TaskUpdate) => apiPatch<Task>(`/api/tasks/${task?.id}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      toast.success("Task updated!", "Your changes have been saved");
      onClose();
    },
    onError: () => {
      toast.error("Failed to update task", "Please try again");
    },
  });

  const isPending = createMutation.isPending || updateMutation.isPending;

  // Add tag
  const handleAddTag = () => {
    const trimmed = tagInput.trim().toLowerCase();
    if (trimmed && !tags.includes(trimmed) && tags.length < 10) {
      setTags([...tags, trimmed]);
      setTagInput("");
    }
  };

  // Remove tag
  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter((t) => t !== tagToRemove));
  };

  // Handle tag input keydown
  const handleTagKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleAddTag();
    } else if (e.key === "Backspace" && !tagInput && tags.length > 0) {
      setTags(tags.slice(0, -1));
    }
  };

  // Validate form
  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    const trimmedTitle = title.trim();
    if (!trimmedTitle) {
      newErrors.title = "Title is required";
    } else if (trimmedTitle.length > 500) {
      newErrors.title = "Title must be 500 characters or less";
    }

    if (description.length > 2000) {
      newErrors.description = "Description must be 2000 characters or less";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Submit form
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) return;

    const formData = {
      title: title.trim(),
      description: description.trim() || null,
      due_date: dueDate || null,
      priority: priority || undefined,
      tags: tags.length > 0 ? tags : undefined,
    };

    if (isEditing) {
      updateMutation.mutate(formData);
    } else {
      createMutation.mutate(formData);
    }
  };

  // Get today's date for min attribute
  const today = new Date().toISOString().split("T")[0];

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={isEditing ? "Edit Task" : "Create New Task"} size="xl">
      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Title */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
            Title <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="What needs to be done?"
            className={`w-full rounded-lg border ${
              errors.title ? "border-red-500" : "border-gray-300 dark:border-gray-600"
            } bg-white dark:bg-gray-900 px-4 py-2.5 text-sm placeholder-gray-400 dark:placeholder-gray-500 dark:text-white focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20`}
            disabled={isPending}
            autoFocus
          />
          <div className="flex justify-between mt-1">
            {errors.title && (
              <span className="text-xs text-red-500">{errors.title}</span>
            )}
            <span className={`text-xs ml-auto ${title.length > 450 ? "text-yellow-500" : "text-gray-400"}`}>
              {title.length}/500
            </span>
          </div>
        </div>

        {/* Description */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
            Description
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Add more details about this task..."
            rows={3}
            className={`w-full rounded-lg border ${
              errors.description ? "border-red-500" : "border-gray-300 dark:border-gray-600"
            } bg-white dark:bg-gray-900 px-4 py-2.5 text-sm placeholder-gray-400 dark:placeholder-gray-500 dark:text-white focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 resize-none`}
            disabled={isPending}
          />
          <div className="flex justify-between mt-1">
            {errors.description && (
              <span className="text-xs text-red-500">{errors.description}</span>
            )}
            <span className={`text-xs ml-auto ${description.length > 1800 ? "text-yellow-500" : "text-gray-400"}`}>
              {description.length}/2000
            </span>
          </div>
        </div>

        {/* Due Date & Priority Row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Due Date */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
              Due Date
            </label>
            <input
              type="date"
              value={dueDate}
              onChange={(e) => setDueDate(e.target.value)}
              min={today}
              className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 px-4 py-2.5 text-sm dark:text-white focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
              disabled={isPending}
            />
          </div>

          {/* Priority */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
              Priority <span className="text-xs text-gray-400">(optional)</span>
            </label>
            <div className="grid grid-cols-4 gap-2">
              {PRIORITY_OPTIONS.map((p) => {
                const config = PRIORITY_CONFIG[p];
                const isSelected = priority === p;
                return (
                  <button
                    key={p}
                    type="button"
                    onClick={() => setPriority(priority === p ? null : p)}
                    disabled={isPending}
                    className={`flex flex-col items-center justify-center py-2 px-1 rounded-lg border-2 transition-all text-xs ${
                      isSelected
                        ? p === "low"
                          ? "border-gray-500 bg-gray-50 dark:bg-gray-800"
                          : p === "medium"
                          ? "border-blue-500 bg-blue-50 dark:bg-blue-900/30"
                          : p === "high"
                          ? "border-orange-500 bg-orange-50 dark:bg-orange-900/30"
                          : "border-red-500 bg-red-50 dark:bg-red-900/30"
                        : "border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600"
                    }`}
                  >
                    <span className="text-base">{config.icon}</span>
                    <span className={`font-medium ${
                      isSelected
                        ? p === "low"
                          ? "text-gray-700 dark:text-gray-300"
                          : p === "medium"
                          ? "text-blue-700 dark:text-blue-300"
                          : p === "high"
                          ? "text-orange-700 dark:text-orange-300"
                          : "text-red-700 dark:text-red-300"
                        : "text-gray-600 dark:text-gray-400"
                    }`}>
                      {config.label}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Tags */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
            Tags <span className="text-xs text-gray-400">(max 10)</span>
          </label>
          <div className="flex flex-wrap gap-2 mb-2">
            {tags.map((tag) => (
              <span
                key={tag}
                className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300"
              >
                #{tag}
                <button
                  type="button"
                  onClick={() => handleRemoveTag(tag)}
                  className="hover:text-blue-900 dark:hover:text-blue-100"
                  disabled={isPending}
                >
                  <svg className="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </span>
            ))}
          </div>
          <div className="flex gap-2">
            <input
              type="text"
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              onKeyDown={handleTagKeyDown}
              placeholder={tags.length >= 10 ? "Max tags reached" : "Add a tag..."}
              className="flex-1 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 px-4 py-2 text-sm placeholder-gray-400 dark:placeholder-gray-500 dark:text-white focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
              disabled={isPending || tags.length >= 10}
            />
            <Button
              type="button"
              variant="outline"
              onClick={handleAddTag}
              disabled={isPending || !tagInput.trim() || tags.length >= 10}
            >
              Add
            </Button>
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-2">
          <Button type="button" variant="outline" onClick={onClose} disabled={isPending}>
            Cancel
          </Button>
          <Button type="submit" isLoading={isPending} disabled={!title.trim()}>
            {isEditing ? "Save Changes" : "Create Task"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
