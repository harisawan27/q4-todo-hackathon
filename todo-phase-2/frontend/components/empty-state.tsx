"use client";

export function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-6 text-center">
      <div className="relative">
        <div className="absolute -inset-4 rounded-full bg-blue-100/50 blur-xl" />
        <div className="relative rounded-2xl bg-gradient-to-br from-blue-100 to-indigo-100 p-6">
          <svg
            className="h-12 w-12 text-blue-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
            />
          </svg>
        </div>
      </div>
      <h3 className="mt-6 text-lg font-semibold text-gray-900">No tasks yet</h3>
      <p className="mt-2 max-w-xs text-sm text-gray-500">
        Get started by creating your first task. Stay organized and boost your productivity!
      </p>
      <div className="mt-6 flex items-center gap-2 text-xs text-gray-400">
        <kbd className="rounded border border-gray-200 bg-gray-100 px-2 py-1 font-mono">
          Tip
        </kbd>
        <span>Add a task using the form above</span>
      </div>
    </div>
  );
}
