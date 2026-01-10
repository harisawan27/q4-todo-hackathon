"use client";

import { getJwtToken } from "./auth-client";

// Safely remove any trailing slash from the base URL
const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/$/, "");

interface ApiOptions extends RequestInit {
  json?: unknown;
}

class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function getAuthHeaders(): Promise<HeadersInit> {
  const token = await getJwtToken();
  const headers: HeadersInit = {
    "Content-Type": "application/json",
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  return headers;
}

export async function api<T>(
  endpoint: string,
  options: ApiOptions = {}
): Promise<T> {
  const { json, ...init } = options;

  // Ensure the endpoint starts with a single slash
  const cleanEndpoint = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
  
  const headers = await getAuthHeaders();

  const config: RequestInit = {
    ...init,
    // CRITICAL: Required for cross-domain cookies (Vercel -> Hugging Face)
    credentials: "include", 
    headers: {
      ...headers,
      ...init.headers,
    },
  };

  if (json !== undefined) {
    config.body = JSON.stringify(json);
  }

  // Final production URL construction
  const response = await fetch(`${API_BASE_URL}${cleanEndpoint}`, config);

  if (!response.ok) {
    const error = await response.json().catch(() => ({
      detail: "An unexpected error occurred",
      code: "UNKNOWN_ERROR",
    }));
    throw new ApiError(
      response.status,
      error.code || "UNKNOWN_ERROR",
      error.detail || "An unexpected error occurred"
    );
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

/**
 * Convenience methods
 */
export const apiGet = <T>(endpoint: string) => api<T>(endpoint, { method: "GET" });

export const apiPost = <T>(endpoint: string, data?: unknown) =>
  api<T>(endpoint, { method: "POST", json: data });

export const apiPut = <T>(endpoint: string, data?: unknown) =>
  api<T>(endpoint, { method: "PUT", json: data });

export const apiPatch = <T>(endpoint: string, data?: unknown) =>
  api<T>(endpoint, { method: "PATCH", json: data });

export const apiDelete = <T>(endpoint: string) =>
  api<T>(endpoint, { method: "DELETE" });

export { ApiError };
