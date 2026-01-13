-- Migration: Add due_time and reminder_level columns
-- Date: 2026-01-13
-- Description:
--   1. Adds due_time field to tasks for specific deadline times
--   2. Adds reminder_level field to notifications for Duolingo-style tiered reminders

-- Add due_time column to tasks (TIME type, nullable)
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS due_time TIME;

-- Add reminder_level column to notifications (VARCHAR, nullable)
-- Values: day_before, hours_10, hours_6, hours_3, hours_1, overdue
ALTER TABLE notifications ADD COLUMN IF NOT EXISTS reminder_level VARCHAR(20);

-- Verify the columns were added
SELECT 'tasks.due_time' as field, column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'tasks' AND column_name = 'due_time'
UNION ALL
SELECT 'notifications.reminder_level' as field, column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'notifications' AND column_name = 'reminder_level';
