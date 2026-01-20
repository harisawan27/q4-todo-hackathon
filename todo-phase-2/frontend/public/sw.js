/**
 * Service Worker for DoneKaro Push Notifications
 * Handles push events and notification clicks
 */

const SW_VERSION = '1.0.0';

// Install event - activate immediately
self.addEventListener('install', (event) => {
  console.log('[SW] Service Worker installing, version:', SW_VERSION);
  self.skipWaiting();
});

// Activate event - claim clients immediately
self.addEventListener('activate', (event) => {
  console.log('[SW] Service Worker activating');
  event.waitUntil(clients.claim());
});

// Push event - show notification when push is received
self.addEventListener('push', (event) => {
  console.log('[SW] Push received');

  if (!event.data) {
    console.log('[SW] Push event has no data');
    return;
  }

  let data;
  try {
    data = event.data.json();
  } catch (e) {
    console.error('[SW] Error parsing push data:', e);
    data = {
      title: 'DoneKaro',
      message: event.data.text(),
    };
  }

  const title = data.title || 'DoneKaro';
  const options = {
    body: data.message || 'You have a new notification',
    icon: '/android-chrome-192x192.png',
    badge: '/favicon-32x32.png',
    tag: data.notification_id || 'default',
    renotify: true,
    requireInteraction: data.type === 'deadline_approaching' || data.type === 'deadline_passed',
    data: {
      url: data.task_id ? `/dashboard/tasks` : '/dashboard',
      notification_id: data.notification_id,
      task_id: data.task_id,
      type: data.type,
    },
    actions: data.task_id
      ? [
          { action: 'view', title: 'View Task' },
          { action: 'dismiss', title: 'Dismiss' },
        ]
      : [],
  };

  // Add urgency-based styling
  if (data.type === 'deadline_passed') {
    options.body = `⚠️ ${options.body}`;
  } else if (data.type === 'deadline_approaching') {
    options.body = `⏰ ${options.body}`;
  } else if (data.type === 'task_completed') {
    options.body = `✅ ${options.body}`;
  }

  event.waitUntil(self.registration.showNotification(title, options));

  // Notify open clients about the new notification
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
      clientList.forEach((client) => {
        client.postMessage({
          type: 'NEW_NOTIFICATION',
          notification_id: data.notification_id,
        });
      });
    })
  );
});

// Notification click event - handle user interaction
self.addEventListener('notificationclick', (event) => {
  console.log('[SW] Notification clicked:', event.action);

  event.notification.close();

  if (event.action === 'dismiss') {
    return;
  }

  const urlToOpen = event.notification.data?.url || '/dashboard';

  event.waitUntil(
    clients
      .matchAll({ type: 'window', includeUncontrolled: true })
      .then((clientList) => {
        // Check if there's already a window open
        for (const client of clientList) {
          if (client.url.includes(self.registration.scope) && 'focus' in client) {
            client.postMessage({
              type: 'NOTIFICATION_CLICKED',
              url: urlToOpen,
              notification_id: event.notification.data?.notification_id,
            });
            return client.focus();
          }
        }

        // No window open, open a new one
        if (clients.openWindow) {
          return clients.openWindow(urlToOpen);
        }
      })
  );
});

// Notification close event
self.addEventListener('notificationclose', (event) => {
  console.log('[SW] Notification closed');
});

// Message event - handle messages from main thread
self.addEventListener('message', (event) => {
  console.log('[SW] Message received:', event.data);

  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
