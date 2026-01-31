package com.donekaro.app;

import android.app.Application;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.os.Build;

/**
 * Main Application class.
 * Creates notification channels at app startup, before any Activity or Service runs.
 * This is critical for FCM background notifications to work when the app is killed.
 */
public class MainApplication extends Application {

    @Override
    public void onCreate() {
        super.onCreate();
        // Create notification channels immediately when app process starts
        createNotificationChannels();
    }

    /**
     * Create notification channels for FCM push notifications.
     * These channels must exist before FCM can display background notifications.
     * Called from Application.onCreate() to ensure channels exist even when app is killed.
     */
    private void createNotificationChannels() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationManager notificationManager = getSystemService(NotificationManager.class);

            // High priority channel for deadline alerts (default FCM channel)
            NotificationChannel deadlineChannel = new NotificationChannel(
                "deadline-alerts",
                "Deadline Alerts",
                NotificationManager.IMPORTANCE_HIGH
            );
            deadlineChannel.setDescription("Important alerts for upcoming and overdue task deadlines");
            deadlineChannel.enableVibration(true);
            deadlineChannel.enableLights(true);
            deadlineChannel.setShowBadge(true);
            notificationManager.createNotificationChannel(deadlineChannel);

            // Default priority channel for task updates
            NotificationChannel taskChannel = new NotificationChannel(
                "task-updates",
                "Task Updates",
                NotificationManager.IMPORTANCE_DEFAULT
            );
            taskChannel.setDescription("General updates about your tasks");
            taskChannel.enableVibration(true);
            taskChannel.setShowBadge(true);
            notificationManager.createNotificationChannel(taskChannel);

            // High priority channel for reminders
            NotificationChannel reminderChannel = new NotificationChannel(
                "reminders",
                "Reminders",
                NotificationManager.IMPORTANCE_HIGH
            );
            reminderChannel.setDescription("Scheduled task reminders");
            reminderChannel.enableVibration(true);
            reminderChannel.enableLights(true);
            reminderChannel.setShowBadge(true);
            notificationManager.createNotificationChannel(reminderChannel);
        }
    }
}
