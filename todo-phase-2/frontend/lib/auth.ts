import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";
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

  advanced: {
    // Allow cross-origin requests from trusted origins
    crossSubDomainCookies: {
      enabled: true,
      domain: ".vercel.app",
    },
  },

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
    }),
  ],
});
