# Better Auth Configuration Skill

## Overview

This skill defines the complete setup for Better Auth with Next.js on Vercel, connecting to Neon PostgreSQL, with FastAPI backend JWT verification. It includes all lessons learned from production debugging.

## Technical Stack

| Layer    | Technology                     |
|----------|--------------------------------|
| Frontend | Next.js 16 (App Router), TypeScript |
| Backend  | FastAPI, SQLModel              |
| Database | Neon PostgreSQL                |
| Auth     | Better-Auth (frontend), python-jose (backend) |
| Hosting  | Vercel (frontend), Hugging Face Spaces (backend) |

---

## 1. Required Packages (Frontend)

```bash
npm install better-auth @neondatabase/serverless
```

**CRITICAL**: Do NOT use `pg` package on Vercel - use `@neondatabase/serverless` instead.

**NEVER install** `ws` package - it's incompatible with Vercel serverless runtime.

---

## 2. Environment Variables

### Frontend (Vercel Dashboard → Settings → Environment Variables)

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | Neon PostgreSQL connection string (use pooler URL) | `postgresql://user:pass@ep-xxx-pooler.region.aws.neon.tech/db?sslmode=require` |
| `BETTER_AUTH_SECRET` | Shared secret for JWT signing (MUST match backend) | `openssl rand -base64 32` |
| `BETTER_AUTH_URL` | Your frontend URL | `https://your-app.vercel.app` |

### Backend (Hugging Face Secrets or .env)

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | Same Neon connection string |
| `BETTER_AUTH_SECRET` | **MUST be identical** to frontend |

---

## 3. Better Auth Server Setup (auth.ts)

```typescript
// lib/auth.ts
import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";
import { nextCookies } from "better-auth/next-js";
import { Pool } from "@neondatabase/serverless";

// Get auth URL from environment
const authUrl = process.env.BETTER_AUTH_URL || "http://localhost:3000";

// Trusted origins - include all deployment URLs
const trustedOrigins = [
  "http://localhost:3000",
  "https://your-app.vercel.app",
  // Add preview deployment URLs if needed
];

// Create Neon serverless pool - NO ws config needed on Vercel
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

  plugins: [
    jwt({
      jwt: {
        expirationTime: "7d",
      },
    }),
    nextCookies(), // MUST be last plugin for Next.js
  ],
});
```

### Critical Points:
1. **Use `@neondatabase/serverless`** - NOT `pg`
2. **Add `nextCookies()` plugin** - MUST be the last plugin
3. **No `ws` WebSocket config** - Vercel handles this natively
4. **trustedOrigins** - List all valid origins (no typos like `https://https://`)

---

## 4. API Route Handler

```typescript
// app/api/auth/[...all]/route.ts
import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

export const { GET, POST } = toNextJsHandler(auth);
```

---

## 5. Auth Client Setup

```typescript
// lib/auth-client.ts
"use client";

import { createAuthClient } from "better-auth/react";
import { jwtClient } from "better-auth/client/plugins";

export const authClient = createAuthClient({
  // Use empty string for relative URLs - avoids hydration mismatch
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
```

---

## 6. Database Tables (Required)

Better Auth requires these tables in your Neon database:

```sql
-- user table
CREATE TABLE IF NOT EXISTS "user" (
  id TEXT PRIMARY KEY,
  name TEXT,
  email TEXT UNIQUE NOT NULL,
  "emailVerified" BOOLEAN DEFAULT FALSE,
  image TEXT,
  "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- session table
CREATE TABLE IF NOT EXISTS "session" (
  id TEXT PRIMARY KEY,
  token TEXT UNIQUE NOT NULL,
  "userId" TEXT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
  "expiresAt" TIMESTAMP NOT NULL,
  "userAgent" TEXT,
  "ipAddress" TEXT,
  "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- account table
CREATE TABLE IF NOT EXISTS "account" (
  id TEXT PRIMARY KEY,
  "accountId" TEXT NOT NULL,
  "providerId" TEXT NOT NULL,
  "userId" TEXT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
  "accessToken" TEXT,
  "refreshToken" TEXT,
  "accessTokenExpiresAt" TIMESTAMP,
  "refreshTokenExpiresAt" TIMESTAMP,
  scope TEXT,
  password TEXT,
  "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- verification table
CREATE TABLE IF NOT EXISTS "verification" (
  id TEXT PRIMARY KEY,
  identifier TEXT NOT NULL,
  value TEXT NOT NULL,
  "expiresAt" TIMESTAMP NOT NULL,
  "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- jwks table (for JWT plugin)
CREATE TABLE IF NOT EXISTS "jwks" (
  id TEXT PRIMARY KEY,
  "publicKey" TEXT NOT NULL,
  "privateKey" TEXT NOT NULL,
  "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_session_userId ON "session"("userId");
CREATE INDEX IF NOT EXISTS idx_account_userId ON "account"("userId");
```

---

## 7. FastAPI JWT Verification (Backend)

```python
# app/auth/jwt_bearer.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel
import os

security = HTTPBearer()

class TokenData(BaseModel):
    user_id: str
    email: str | None = None

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenData:
    token = credentials.credentials
    secret = os.getenv("BETTER_AUTH_SECRET")

    if not secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Auth secret not configured"
        )

    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        email: str | None = payload.get("email")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing sub claim"
            )

        return TokenData(user_id=user_id, email=email)

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {str(e)}"
        )
```

---

## 8. Common Errors & Solutions

### ERR_HTTP2_PROTOCOL_ERROR / Failed to Fetch

| Cause | Solution |
|-------|----------|
| Using `pg` package on Vercel | Switch to `@neondatabase/serverless` |
| Using `ws` package | Remove it - Vercel has native WebSocket |
| Missing `nextCookies()` plugin | Add as the last plugin |
| Environment variables not set | Check Vercel Dashboard → Settings → Environment Variables |
| Database tables missing | Run the CREATE TABLE scripts above |

### Invalid Origin Error

| Cause | Solution |
|-------|----------|
| Typo in trustedOrigins (e.g., `https://https://`) | Fix the URL |
| Missing production URL | Add your Vercel URL to trustedOrigins |
| Preview deployment URL not included | Add preview URLs or use regex pattern |

### Hydration Mismatch (React Error #418)

| Cause | Solution |
|-------|----------|
| Using `window.location.origin` in auth-client | Use `baseURL: ""` for relative URLs |
| Different server/client rendering | Ensure consistent baseURL |

### Accounts Created Locally Don't Work in Production

| Cause | Solution |
|-------|----------|
| Different `BETTER_AUTH_SECRET` | Password hashes are tied to secret - create new accounts |

---

## 9. Debugging Checklist

Before deploying, verify:

- [ ] `@neondatabase/serverless` installed (NOT `pg`)
- [ ] `ws` package NOT installed
- [ ] `nextCookies()` plugin added as LAST plugin
- [ ] `BETTER_AUTH_SECRET` set in Vercel (not just .env.local)
- [ ] `DATABASE_URL` set in Vercel
- [ ] `BETTER_AUTH_URL` set to production URL
- [ ] All 5 database tables exist (user, session, account, verification, jwks)
- [ ] trustedOrigins includes production URL (no typos)
- [ ] Backend has SAME `BETTER_AUTH_SECRET`

---

## 10. Debug Endpoint (For Troubleshooting)

Create a temporary debug endpoint to verify setup:

```typescript
// app/api/debug/route.ts
import { NextResponse } from "next/server";
import { Pool } from "@neondatabase/serverless";

export async function GET() {
  const results = {
    env: {
      DATABASE_URL: process.env.DATABASE_URL ? "SET" : "NOT SET",
      BETTER_AUTH_SECRET: process.env.BETTER_AUTH_SECRET ? "SET" : "NOT SET",
      BETTER_AUTH_URL: process.env.BETTER_AUTH_URL || "NOT SET",
    },
    database: { connection: "UNTESTED", tables: {} },
  };

  try {
    const pool = new Pool({ connectionString: process.env.DATABASE_URL });
    await pool.query("SELECT 1");
    results.database.connection = "OK";

    const tables = ["user", "session", "account", "verification", "jwks"];
    for (const table of tables) {
      try {
        const r = await pool.query(`SELECT COUNT(*) FROM "${table}"`);
        results.database.tables[table] = `EXISTS (${r.rows[0].count} rows)`;
      } catch {
        results.database.tables[table] = "MISSING";
      }
    }
    await pool.end();
  } catch (e) {
    results.database.connection = "FAILED: " + e.message;
  }

  return NextResponse.json(results);
}
```

**Delete this endpoint before production!**

---

## 11. SQLModel Query Enforcement Rule

**MANDATORY**: All queries MUST filter by `user_id` from JWT:

```python
# CORRECT
@router.get("/todos")
def get_todos(
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    statement = select(Todo).where(Todo.user_id == current_user.user_id)
    return session.exec(statement).all()

# WRONG - SECURITY VULNERABILITY
@router.get("/todos")
def get_todos_INSECURE(session: Session = Depends(get_session)):
    return session.exec(select(Todo)).all()  # NO USER FILTER!
```

---

## 12. Validation Checklist

Before any route is approved:

- [ ] Route has `Depends(get_current_user)` dependency
- [ ] All SQLModel queries include `.where(...user_id == current_user.user_id)`
- [ ] No raw SQL without user_id parameterization
- [ ] Frontend sends `Authorization: Bearer <token>` header
- [ ] Both frontend and backend use identical `BETTER_AUTH_SECRET`
