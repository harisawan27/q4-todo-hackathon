"use client";

import { createAuthClient } from "better-auth/react";
import { jwtClient } from "better-auth/client/plugins";
import { useRouter } from "next/navigation";
import { useEffect, useCallback } from "react";

export const authClient = createAuthClient({
  // Use empty string for relative URLs - Better Auth handles this correctly
  // This avoids hydration mismatch between server and client
  baseURL: "",
  plugins: [jwtClient()],
});

export const {
  signIn,
  signUp,
  signOut,
  useSession,
  getSession,
} = authClient;

/**
 * Get JWT token for API calls
 */
export async function getJwtToken(): Promise<string | null> {
  try {
    const response = await fetch("/api/auth/token", {
      credentials: "include",
    });
    if (!response.ok) {
      return null;
    }
    const data = await response.json();
    return data?.token || null;
  } catch {
    return null;
  }
}

/**
 * Hook to protect routes - redirects to /sign-in if no valid session
 */
export function useRequireAuth() {
  const router = useRouter();
  const { data: session, isPending, error } = useSession();

  const handleSessionExpired = useCallback(() => {
    // Store a message to show on the sign-in page
    if (typeof window !== "undefined") {
      sessionStorage.setItem("sessionExpiredMessage", "Your session has expired. Please sign in again.");
    }
    router.push("/sign-in");
  }, [router]);

  useEffect(() => {
    if (!isPending && !session) {
      // Check if this was a session expiration (had a session before)
      if (error) {
        handleSessionExpired();
      } else {
        router.push("/sign-in");
      }
    }
  }, [session, isPending, error, router, handleSessionExpired]);

  return { session, isPending, isAuthenticated: !!session };
}

/**
 * Hook to get and clear session expired message
 */
export function useSessionExpiredMessage() {
  useEffect(() => {
    // Clear the message after it's been shown
    return () => {
      if (typeof window !== "undefined") {
        sessionStorage.removeItem("sessionExpiredMessage");
      }
    };
  }, []);

  if (typeof window === "undefined") {
    return null;
  }

  return sessionStorage.getItem("sessionExpiredMessage");
}
