package com.donekaro.app;

import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.media.RingtoneManager;
import android.net.Uri;
import android.os.Build;
import android.util.Log;

import androidx.annotation.NonNull;
import androidx.core.app.NotificationCompat;

import com.google.firebase.messaging.FirebaseMessagingService;
import com.google.firebase.messaging.RemoteMessage;

import java.util.Map;

/**
 * Custom Firebase Messaging Service for DoneKaro app.
 *
 * This service handles FCM messages when the app is in background or killed.
 * It ensures notifications are always displayed, even when the Capacitor
 * plugin can't handle them (app killed state).
 */
public class DoneKaroMessagingService extends FirebaseMessagingService {

    private static final String TAG = "DoneKaroFCM";

    // Notification channels (must match MainApplication.java)
    private static final String CHANNEL_DEADLINE_ALERTS = "deadline-alerts";
    private static final String CHANNEL_TASK_UPDATES = "task-updates";
    private static final String CHANNEL_REMINDERS = "reminders";

    // Notification types from backend
    private static final String TYPE_DEADLINE_APPROACHING = "deadline_approaching";
    private static final String TYPE_DEADLINE_PASSED = "deadline_passed";
    private static final String TYPE_TASK_CREATED = "task_created";
    private static final String TYPE_TASK_COMPLETED = "task_completed";
    private static final String TYPE_TASK_DELETED = "task_deleted";
    private static final String TYPE_TEST = "test";

    @Override
    public void onMessageReceived(@NonNull RemoteMessage remoteMessage) {
        Log.d(TAG, "FCM message received from: " + remoteMessage.getFrom());

        // Get notification data
        Map<String, String> data = remoteMessage.getData();
        RemoteMessage.Notification notification = remoteMessage.getNotification();

        String title = null;
        String body = null;

        // Extract title and body from notification payload (if present)
        if (notification != null) {
            title = notification.getTitle();
            body = notification.getBody();
            Log.d(TAG, "Notification payload - Title: " + title + ", Body: " + body);
        }

        // Also check data payload for title/body (fallback)
        if (title == null && data.containsKey("title")) {
            title = data.get("title");
        }
        if (body == null && data.containsKey("body")) {
            body = data.get("body");
        }
        if (body == null && data.containsKey("message")) {
            body = data.get("message");
        }

        // Default values if still null
        if (title == null) {
            title = "DoneKaro";
        }
        if (body == null) {
            body = "You have a new notification";
        }

        // Get notification type for channel selection
        String type = data.get("type");
        String taskId = data.get("task_id");
        String notificationId = data.get("notification_id");

        Log.d(TAG, "Data payload - Type: " + type + ", TaskId: " + taskId + ", NotificationId: " + notificationId);

        // Always show notification (this ensures it shows even when app is killed)
        showNotification(title, body, type, taskId, notificationId);

        // Also try to forward to Capacitor plugin (for foreground handling)
        try {
            com.capacitorjs.plugins.pushnotifications.PushNotificationsPlugin.sendRemoteMessage(remoteMessage);
        } catch (Exception e) {
            Log.d(TAG, "Could not forward to Capacitor plugin (app may be in background): " + e.getMessage());
        }
    }

    @Override
    public void onNewToken(@NonNull String token) {
        Log.d(TAG, "FCM token refreshed: " + token.substring(0, Math.min(20, token.length())) + "...");

        // Forward to Capacitor plugin for token registration
        try {
            com.capacitorjs.plugins.pushnotifications.PushNotificationsPlugin.onNewToken(token);
        } catch (Exception e) {
            Log.d(TAG, "Could not forward token to Capacitor plugin: " + e.getMessage());
        }
    }

    /**
     * Show a notification in the system tray.
     * This method ensures notifications are visible even when the app is killed.
     */
    private void showNotification(String title, String body, String type, String taskId, String notificationId) {
        Log.d(TAG, "Showing notification - Title: " + title);

        // Select channel based on notification type
        String channelId = selectChannel(type);

        // Create intent for when notification is tapped
        Intent intent = new Intent(this, MainActivity.class);
        intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP);

        // Add data for handling in the app
        if (taskId != null && !taskId.isEmpty()) {
            intent.putExtra("task_id", taskId);
            intent.putExtra("navigate_to", "tasks");
        }
        if (notificationId != null && !notificationId.isEmpty()) {
            intent.putExtra("notification_id", notificationId);
        }
        if (type != null) {
            intent.putExtra("notification_type", type);
        }

        // Create unique notification ID
        int uniqueNotificationId = (int) System.currentTimeMillis();
        if (notificationId != null && !notificationId.isEmpty()) {
            try {
                uniqueNotificationId = notificationId.hashCode();
            } catch (Exception ignored) {}
        }

        // Create pending intent
        int flags = PendingIntent.FLAG_UPDATE_CURRENT;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            flags |= PendingIntent.FLAG_IMMUTABLE;
        }
        PendingIntent pendingIntent = PendingIntent.getActivity(this, uniqueNotificationId, intent, flags);

        // Get default sound
        Uri defaultSoundUri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);

        // Build notification
        NotificationCompat.Builder notificationBuilder = new NotificationCompat.Builder(this, channelId)
                .setSmallIcon(R.mipmap.ic_launcher)
                .setContentTitle(title)
                .setContentText(body)
                .setAutoCancel(true)
                .setSound(defaultSoundUri)
                .setContentIntent(pendingIntent)
                .setPriority(getPriority(type))
                .setCategory(NotificationCompat.CATEGORY_REMINDER);

        // Add vibration for urgent notifications
        if (isUrgent(type)) {
            notificationBuilder.setVibrate(new long[]{0, 500, 250, 500});
        }

        // For longer messages, use big text style
        if (body != null && body.length() > 50) {
            notificationBuilder.setStyle(new NotificationCompat.BigTextStyle().bigText(body));
        }

        // Show notification
        NotificationManager notificationManager = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
        if (notificationManager != null) {
            notificationManager.notify(uniqueNotificationId, notificationBuilder.build());
            Log.d(TAG, "Notification displayed with ID: " + uniqueNotificationId);
        } else {
            Log.e(TAG, "NotificationManager is null, cannot show notification");
        }
    }

    /**
     * Select the appropriate notification channel based on notification type.
     */
    private String selectChannel(String type) {
        if (type == null) {
            return CHANNEL_TASK_UPDATES;
        }

        switch (type) {
            case TYPE_DEADLINE_APPROACHING:
            case TYPE_DEADLINE_PASSED:
                return CHANNEL_DEADLINE_ALERTS;
            case TYPE_TASK_CREATED:
            case TYPE_TASK_COMPLETED:
            case TYPE_TASK_DELETED:
            case TYPE_TEST:
            default:
                return CHANNEL_TASK_UPDATES;
        }
    }

    /**
     * Get notification priority based on type.
     */
    private int getPriority(String type) {
        if (type == null) {
            return NotificationCompat.PRIORITY_DEFAULT;
        }

        switch (type) {
            case TYPE_DEADLINE_APPROACHING:
            case TYPE_DEADLINE_PASSED:
                return NotificationCompat.PRIORITY_HIGH;
            default:
                return NotificationCompat.PRIORITY_DEFAULT;
        }
    }

    /**
     * Check if notification is urgent (for vibration).
     */
    private boolean isUrgent(String type) {
        if (type == null) {
            return false;
        }
        return type.equals(TYPE_DEADLINE_APPROACHING) || type.equals(TYPE_DEADLINE_PASSED);
    }
}
