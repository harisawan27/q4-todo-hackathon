"use client";

import { useEffect, useRef, useCallback } from "react";
import { useQueryClient } from "@tanstack/react-query";

const MAX_RECONNECT_DELAY = 30000;
const INITIAL_RECONNECT_DELAY = 1000;

export function useTaskUpdates(userId: string | null) {
  const queryClient = useQueryClient();
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectDelayRef = useRef(INITIAL_RECONNECT_DELAY);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const connect = useCallback(() => {
    if (!userId) return;

    // Clean up existing connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    const url = `/api/events/stream`;
    const eventSource = new EventSource(url, { withCredentials: true });
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      console.log("[SSE] Connected to task updates stream");
      reconnectDelayRef.current = INITIAL_RECONNECT_DELAY;
    };

    eventSource.addEventListener("task-update", (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log("[SSE] Task update received:", data.action, data.taskId);

        // Invalidate tasks query to trigger refetch
        queryClient.invalidateQueries({ queryKey: ["tasks"] });

        // If a specific task was updated, also invalidate that task's query
        if (data.taskId) {
          queryClient.invalidateQueries({ queryKey: ["tasks", data.taskId] });
          queryClient.invalidateQueries({ queryKey: ["audit", data.taskId] });
        }
      } catch (err) {
        console.error("[SSE] Failed to parse task update:", err);
      }
    });

    eventSource.addEventListener("heartbeat", () => {
      // Keepalive — no action needed
    });

    eventSource.onerror = (err) => {
      console.error("[SSE] Connection error:", err);
      eventSource.close();
      eventSourceRef.current = null;

      // Exponential backoff reconnect
      const delay = reconnectDelayRef.current;
      console.log(`[SSE] Reconnecting in ${delay}ms...`);
      reconnectTimerRef.current = setTimeout(() => {
        reconnectDelayRef.current = Math.min(delay * 2, MAX_RECONNECT_DELAY);
        connect();
      }, delay);
    };
  }, [userId, queryClient]);

  useEffect(() => {
    connect();

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
        reconnectTimerRef.current = null;
      }
    };
  }, [connect]);
}
