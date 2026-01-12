import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";
import { Pool } from "pg";

// Validate required environment variables
if (!process.env.DATABASE_URL) {
  console.error("[Better Auth] ERROR: DATABASE_URL is not set!");
}
if (!process.env.BETTER_AUTH_SECRET) {
  console.error("[Better Auth] ERROR: BETTER_AUTH_SECRET is not set!");
}

// Create pool with Neon-optimized settings for serverless
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: {
    rejectUnauthorized: false,
  },
  // Serverless-optimized settings
  max: 1, // Single connection for serverless
  connectionTimeoutMillis: 10000,
  idleTimeoutMillis: 10000,
});

// Handle pool errors gracefully
pool.on("error", (err) => {
  console.error("[Better Auth] Database pool error:", err.message);
});

// Get auth URL from environment
const authUrl = process.env.BETTER_AUTH_URL || "http://localhost:3000";

// Trusted origins - hardcoded for reliability
const trustedOrigins = [
  "http://localhost:3000",
  "https://q4-todo-hackathon.vercel.app",
];

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
