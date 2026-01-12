import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";
import { Pool } from "pg";

// Debug: Log environment variables (remove in production)
console.log("[Better Auth] Initializing with config:", {
  DATABASE_URL: process.env.DATABASE_URL ? "SET" : "NOT SET",
  BETTER_AUTH_SECRET: process.env.BETTER_AUTH_SECRET ? "SET" : "NOT SET",
  BETTER_AUTH_URL: process.env.BETTER_AUTH_URL || "NOT SET (using default)",
});

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: {
    rejectUnauthorized: false, // Essential for Neon/Vercel compatibility
  },
  connectionTimeoutMillis: 5000,
  idleTimeoutMillis: 30000,
});

// Get auth URL from environment (defaults to localhost for development)
const authUrl = process.env.BETTER_AUTH_URL || "http://localhost:3000";

// Build trusted origins - include both localhost and production
const trustedOrigins = [
  "http://localhost:3000",
  "https://q4-todo-hackathon.vercel.app",
];

// Add authUrl if it's different
if (authUrl && !trustedOrigins.includes(authUrl)) {
  trustedOrigins.push(authUrl);
}

console.log("[Better Auth] baseURL:", authUrl);
console.log("[Better Auth] trustedOrigins:", trustedOrigins);

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
    }),
  ],
});
