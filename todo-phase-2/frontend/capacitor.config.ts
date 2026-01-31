import type { CapacitorConfig } from "@capacitor/cli";

const config: CapacitorConfig = {
  appId: "com.donekaro.app",
  appName: "DoneKaro",
  webDir: "out",
  server: {
    // Load the deployed Vercel app directly
    url: "https://q4-todo-hackathon.vercel.app",
    cleartext: false,
    // Allow Capacitor bridge to work with remote URL
    androidScheme: "https",
    // Show custom offline page when server can't be reached
    errorPath: "offline.html",
  },
  android: {
    // Better web experience
    backgroundColor: "#ffffff",
    allowMixedContent: false,
    captureInput: true,
    webContentsDebuggingEnabled: false,
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 2000,
      backgroundColor: "#ffffff",
      showSpinner: false,
      androidScaleType: "CENTER_CROP",
    },
    GoogleAuth: {
      scopes: ["profile", "email"],
      serverClientId: process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || "",
      forceCodeForRefreshToken: true,
    },
    PushNotifications: {
      presentationOptions: ["badge", "sound", "alert"],
    },
  },
};

export default config;
