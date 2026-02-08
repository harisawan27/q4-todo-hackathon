import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";
import { nextCookies } from "better-auth/next-js";
import { Pool } from "@neondatabase/serverless";

// Google OAuth configuration
const googleClientId = process.env.GOOGLE_CLIENT_ID;
const googleClientSecret = process.env.GOOGLE_CLIENT_SECRET;

// Get auth URL from environment
const authUrl = process.env.BETTER_AUTH_URL || "http://localhost:3000";

// Trusted origins - include production and preview deployments
const trustedOrigins = [
  "http://localhost:3000",
  "https://q4-todo-hackathon.vercel.app",
  "https://taskflow-ajf1nt772-muhammad-haris-awans-projects.vercel.app",
];

// Create Neon serverless pool - no ws config needed on Vercel
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

export const auth = betterAuth({
  secret: process.env.BETTER_AUTH_SECRET,
  baseURL: authUrl,
  database: pool,
  trustedOrigins,

  emailAndPassword: {
    enabled: true,
  },

  // Google OAuth - only enable if credentials are configured
  ...(googleClientId && googleClientSecret
    ? {
        socialProviders: {
          google: {
            clientId: googleClientId,
            clientSecret: googleClientSecret,
          },
        },
      }
    : {}),
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // 1 day
    cookieCache: {
      enabled: true,
      maxAge: 5 * 60,
    },
    // Force fresh user data fetch on each session request
    // This ensures image updates are reflected immediately
    freshAge: 0,
  },
  user: {
    changeEmail: {
      enabled: true,
    },
    deleteUser: {
      enabled: true,
    },
    // IMPORTANT: Do NOT include image in session to prevent header overflow
    // Images are base64 data and will exceed Vercel's 16KB header limit
    // Fetch images separately via API instead
    additionalFields: {
      image: {
        type: "string",
        required: false,
        // CRITICAL: Set to false to exclude from session/JWT/cookies
        returned: false,
      },
    },
  },
  plugins: [
    jwt({
      jwt: {
        expirationTime: "7d",
      },
    }),
    nextCookies(), // Must be last plugin for Next.js cookie handling
  ],
});
