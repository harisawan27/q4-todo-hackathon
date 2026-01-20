/**
 * Centralized date/time utilities for proper UTC-to-local timezone handling
 * All dates are stored in UTC in the backend, displayed in user's local timezone
 */

/**
 * Format a UTC date string to user's local date
 */
export function formatLocalDate(
  utcDateString: string,
  options?: Intl.DateTimeFormatOptions
): string {
  // Ensure we're parsing as UTC by adding Z if not present
  const dateStr = utcDateString.includes("T")
    ? utcDateString
    : `${utcDateString}T00:00:00`;
  const date = new Date(dateStr.endsWith("Z") ? dateStr : `${dateStr}Z`);

  const defaultOptions: Intl.DateTimeFormatOptions = {
    year: "numeric",
    month: "short",
    day: "numeric",
  };

  return new Intl.DateTimeFormat(undefined, options || defaultOptions).format(
    date
  );
}

/**
 * Format a UTC time string to user's local time
 * Input: date (YYYY-MM-DD) + time (HH:MM:SS) both in UTC
 * Output: "2:30 PM" (local)
 */
export function formatLocalTime(
  dateString: string,
  timeString: string | null
): string {
  if (!timeString) return "";

  // Combine date and time into full UTC datetime
  const utcDateTime = new Date(`${dateString}T${timeString}Z`);

  return new Intl.DateTimeFormat(undefined, {
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  }).format(utcDateTime);
}

/**
 * Check if a date is today, tomorrow, overdue, or upcoming (in local timezone)
 */
export function getDueDateStatus(
  dueDateUtc: string | null,
  dueTimeUtc: string | null = null
): "overdue" | "today" | "tomorrow" | "upcoming" | "none" {
  if (!dueDateUtc) return "none";

  const now = new Date();

  // Create the due datetime in UTC, then compare in local
  const dueDateTime = dueTimeUtc
    ? new Date(`${dueDateUtc}T${dueTimeUtc}Z`)
    : new Date(`${dueDateUtc}T23:59:59Z`);

  // For date comparison, use local dates
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const tomorrow = new Date(today);
  tomorrow.setDate(tomorrow.getDate() + 1);
  const dayAfterTomorrow = new Date(tomorrow);
  dayAfterTomorrow.setDate(dayAfterTomorrow.getDate() + 1);

  const localDueDate = new Date(
    dueDateTime.getFullYear(),
    dueDateTime.getMonth(),
    dueDateTime.getDate()
  );

  // Check if overdue (past the due datetime)
  if (dueDateTime.getTime() < now.getTime()) return "overdue";

  // Check if today
  if (localDueDate.getTime() === today.getTime()) return "today";

  // Check if tomorrow
  if (localDueDate.getTime() === tomorrow.getTime()) return "tomorrow";

  return "upcoming";
}

/**
 * Format due date with intelligent relative display
 * Shows "Today", "Tomorrow", or formatted date, with optional time
 */
export function formatDueDateTime(
  dueDateUtc: string | null,
  dueTimeUtc: string | null
): string {
  if (!dueDateUtc) return "";

  const now = new Date();
  const status = getDueDateStatus(dueDateUtc, dueTimeUtc);

  let dateStr: string;
  switch (status) {
    case "today":
      dateStr = "Today";
      break;
    case "tomorrow":
      dateStr = "Tomorrow";
      break;
    default:
      // Format as "Jan 15" or "Jan 15, 2025" if different year
      const dueDate = new Date(`${dueDateUtc}T00:00:00Z`);
      const localDueDate = new Date(
        dueDate.getFullYear(),
        dueDate.getMonth(),
        dueDate.getDate()
      );

      dateStr = new Intl.DateTimeFormat(undefined, {
        month: "short",
        day: "numeric",
        year:
          localDueDate.getFullYear() !== now.getFullYear()
            ? "numeric"
            : undefined,
      }).format(localDueDate);
  }

  // Append time if set
  if (dueTimeUtc) {
    const timeStr = formatLocalTime(dueDateUtc, dueTimeUtc);
    return `${dateStr} at ${timeStr}`;
  }

  return dateStr;
}

/**
 * Calculate hours remaining until deadline
 * Returns null if > 24 hours or no time set
 */
export function getHoursRemaining(
  dueDateUtc: string | null,
  dueTimeUtc: string | null
): number | null {
  if (!dueDateUtc) return null;

  const now = new Date();
  const deadline = dueTimeUtc
    ? new Date(`${dueDateUtc}T${dueTimeUtc}Z`)
    : new Date(`${dueDateUtc}T23:59:59Z`);

  const msRemaining = deadline.getTime() - now.getTime();

  // Only show if within next 24 hours and not yet passed
  if (msRemaining <= 0 || msRemaining > 24 * 60 * 60 * 1000) {
    return null;
  }

  return Math.floor(msRemaining / (1000 * 60 * 60));
}

/**
 * Format relative time (e.g., "2 hours ago", "in 3 days")
 */
export function formatRelativeTime(utcDateString: string): string {
  const dateStr = utcDateString.endsWith("Z")
    ? utcDateString
    : `${utcDateString}Z`;
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSecs = Math.floor(Math.abs(diffMs) / 1000);
  const isPast = diffMs > 0;

  // Use Intl.RelativeTimeFormat for proper localization
  const rtf = new Intl.RelativeTimeFormat(undefined, { numeric: "auto" });

  if (diffSecs < 60) return "Just now";

  if (diffSecs < 3600) {
    const mins = Math.floor(diffSecs / 60);
    return rtf.format(isPast ? -mins : mins, "minute");
  }

  if (diffSecs < 86400) {
    const hours = Math.floor(diffSecs / 3600);
    return rtf.format(isPast ? -hours : hours, "hour");
  }

  if (diffSecs < 604800) {
    const days = Math.floor(diffSecs / 86400);
    return rtf.format(isPast ? -days : days, "day");
  }

  // For older dates, show the actual date
  return formatLocalDate(utcDateString, {
    month: "short",
    day: "numeric",
  });
}

/**
 * Get user's timezone name for display
 */
export function getUserTimezone(): string {
  return Intl.DateTimeFormat().resolvedOptions().timeZone;
}

/**
 * Format a created_at timestamp for display
 */
export function formatCreatedAt(utcDateString: string): string {
  const dateStr = utcDateString.endsWith("Z")
    ? utcDateString
    : `${utcDateString}Z`;
  const date = new Date(dateStr);

  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
  }).format(date);
}
