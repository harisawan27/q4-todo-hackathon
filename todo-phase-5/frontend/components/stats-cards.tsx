"use client";

import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api";
import type { Task } from "@/types/task";

interface StatCardProps {
  title: string;
  value: number;
  icon: React.ReactNode;
  trend?: { value: number; isUp: boolean };
  color: "blue" | "green" | "yellow" | "purple";
  pulsing?: boolean;
}

const colorClasses = {
  blue: {
    bg: "bg-blue-50 dark:bg-blue-900/20",
    icon: "bg-blue-100 dark:bg-blue-900/50 text-blue-600 dark:text-blue-400",
    value: "text-blue-700 dark:text-blue-300",
  },
  green: {
    bg: "bg-green-50 dark:bg-green-900/20",
    icon: "bg-green-100 dark:bg-green-900/50 text-green-600 dark:text-green-400",
    value: "text-green-700 dark:text-green-300",
  },
  yellow: {
    bg: "bg-yellow-50 dark:bg-yellow-900/20",
    icon: "bg-yellow-100 dark:bg-yellow-900/50 text-yellow-600 dark:text-yellow-400",
    value: "text-yellow-700 dark:text-yellow-300",
  },
  purple: {
    bg: "bg-purple-50 dark:bg-purple-900/20",
    icon: "bg-purple-100 dark:bg-purple-900/50 text-purple-600 dark:text-purple-400",
    value: "text-purple-700 dark:text-purple-300",
  },
};

function StatCard({ title, value, icon, trend, color, pulsing }: StatCardProps) {
  const colors = colorClasses[color];

  return (
    <div
      className={`rounded-xl ${pulsing ? "" : colors.bg} p-2 sm:p-5 transition-all hover:shadow-md ${
        pulsing ? "animate-attention-pulse" : ""
      }`}
    >
      {/* Mobile layout: compact vertical stack */}
      <div className="flex flex-col items-center text-center sm:block sm:text-left">
        <div className={`rounded-lg ${colors.icon} p-1.5 sm:p-2.5 [&_svg]:h-4 [&_svg]:w-4 sm:[&_svg]:h-5 sm:[&_svg]:w-5`}>{icon}</div>
        {/* Trend badge - hidden on mobile for space */}
        {trend && (
          <span
            className={`hidden sm:flex items-center gap-1 text-xs font-medium absolute top-2 right-2 ${
              trend.isUp ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"
            }`}
          >
            <svg
              className={`h-3 w-3 ${trend.isUp ? "" : "rotate-180"}`}
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M5.293 7.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L6.707 7.707a1 1 0 01-1.414 0z"
                clipRule="evenodd"
              />
            </svg>
            {trend.value}%
          </span>
        )}
      </div>
      <div className="mt-1 sm:mt-4 text-center sm:text-left">
        <h3 className="text-[10px] sm:text-sm font-medium text-gray-600 dark:text-gray-400 leading-tight">{title}</h3>
        <p className={`mt-0.5 sm:mt-1 text-base sm:text-2xl font-bold ${colors.value}`}>{value}</p>
      </div>
    </div>
  );
}

export function StatsCards() {
  const { data: tasks, isLoading } = useQuery<Task[]>({
    queryKey: ["tasks"],
    queryFn: () => apiGet<Task[]>("/api/tasks"),
  });

  if (isLoading) {
    return (
      <div className="grid grid-cols-4 gap-2 sm:gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-20 sm:h-28 rounded-xl skeleton" />
        ))}
      </div>
    );
  }

  const totalTasks = tasks?.length || 0;
  const completedTasks = tasks?.filter((t) => t.completed).length || 0;
  const pendingTasks = totalTasks - completedTasks;
  const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

  return (
    <div className="grid grid-cols-4 gap-2 sm:gap-4">
      <StatCard
        title="Total Tasks"
        value={totalTasks}
        color="blue"
        icon={
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
        }
      />
      <StatCard
        title="Completed"
        value={completedTasks}
        color="green"
        icon={
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        }
      />
      <StatCard
        title="In Progress"
        value={pendingTasks}
        color="yellow"
        pulsing={pendingTasks > 0}
        icon={
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        }
      />
      <StatCard
        title="Completion Rate"
        value={completionRate}
        color="purple"
        trend={completionRate > 50 ? { value: completionRate, isUp: true } : undefined}
        icon={
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
        }
      />
    </div>
  );
}
