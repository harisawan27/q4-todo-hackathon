"use client";

import { useState, useEffect } from "react";
import { signIn } from "@/lib/auth-client";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";

interface GoogleSignInButtonProps {
  mode?: "signin" | "signup";
}

// Check if running in Capacitor native app
function isNativeApp(): boolean {
  if (typeof window === "undefined") return false;
  return !!(window as any).Capacitor?.isNativePlatform?.();
}

export function GoogleSignInButton({ mode = "signin" }: GoogleSignInButtonProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [isNative, setIsNative] = useState(false);
  const router = useRouter();

  useEffect(() => {
    setIsNative(isNativeApp());
  }, []);

  const handleNativeGoogleSignIn = async () => {
    try {
      // Dynamically import Capacitor Google Auth
      const { GoogleAuth } = await import("@codetrix-studio/capacitor-google-auth");

      // Initialize GoogleAuth
      await GoogleAuth.initialize({
        clientId: "39470081482-sno1ch3sj5qiueb0pk2t8nghtcqf5qde.apps.googleusercontent.com",
        scopes: ["profile", "email"],
        grantOfflineAccess: true,
      });

      // Trigger native Google Sign-In
      const result = await GoogleAuth.signIn();

      if (result.authentication?.idToken) {
        // Send ID token to our backend
        const response = await fetch("/api/auth/native-google", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify({
            idToken: result.authentication.idToken,
          }),
        });

        if (response.ok) {
          // Redirect to dashboard on success
          router.push("/dashboard");
          router.refresh();
        } else {
          const data = await response.json();
          throw new Error(data.error || "Authentication failed");
        }
      } else {
        throw new Error("No ID token received from Google");
      }
    } catch (err: any) {
      console.error("Native Google Sign-In error:", err);
      throw err;
    }
  };

  const handleGoogleSignIn = async () => {
    setError("");
    setIsLoading(true);

    try {
      if (isNative) {
        // Use native Google Sign-In in the app
        await handleNativeGoogleSignIn();
      } else {
        // Use standard web OAuth
        await signIn.social({
          provider: "google",
          callbackURL: "/dashboard",
        });
      }
    } catch (err: any) {
      setError(err.message || "Failed to sign in with Google. Please try again.");
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-3">
      {error && (
        <div className="flex items-center gap-2 rounded-lg bg-red-50 border border-red-100 px-4 py-3">
          <svg className="h-5 w-5 text-red-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}
      <Button
        type="button"
        variant="outline"
        className="w-full"
        size="lg"
        onClick={handleGoogleSignIn}
        isLoading={isLoading}
      >
        {!isLoading && (
          <svg className="mr-2 h-5 w-5" viewBox="0 0 24 24">
            <path
              fill="#4285F4"
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
            />
            <path
              fill="#34A853"
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
            />
            <path
              fill="#FBBC05"
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
            />
            <path
              fill="#EA4335"
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
            />
          </svg>
        )}
        {mode === "signin" ? "Sign in with Google" : "Sign up with Google"}
      </Button>
    </div>
  );
}
