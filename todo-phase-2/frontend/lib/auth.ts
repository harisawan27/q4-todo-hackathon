import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";
import { nextCookies } from "better-auth/next-js";
import { Pool } from "@neondatabase/serverless";

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
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // 1 day
    cookieCache: {
      enabled: true,
      maxAge: 5 * 60,
    },
  },
  user: {
    changeEmail: {
      enabled: true,
    },
    deleteUser: {
      enabled: true,
    },
  },
  plugins: [
    jwt({
      jwt: {
        expirationTime: "7d",
      },
      // Exclude large fields from JWT payload to prevent header size issues
      // Image URLs are stored in DB and fetched via session, not in token
      schema: {
        user: {
          fields: {
            image: false, // Exclude base64 images from JWT to prevent header overflow
          },
        },
      },
    }),
    nextCookies(), // Must be last plugin for Next.js cookie handling
  ],
});
