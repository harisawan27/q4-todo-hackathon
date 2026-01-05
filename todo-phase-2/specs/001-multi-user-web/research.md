# Research: Phase II Multi-User Web Todo Application

**Branch**: `001-multi-user-web` | **Date**: 2026-01-05

## Research Questions Addressed

### 1. Better-Auth JWT Integration with FastAPI

**Decision**: Use shared `BETTER_AUTH_SECRET` with HS256 algorithm for JWT verification.

**Rationale**:
- Better-Auth issues JWTs signed with HMAC-SHA256 using the configured secret
- python-jose can verify these tokens using the same secret and algorithm
- The `sub` claim contains the user ID, which becomes the canonical identifier
- No need for asymmetric keys (RS256) for single-tenant applications

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| RS256 asymmetric keys | Unnecessary complexity for single deployment |
| Session-based auth | Doesn't work well with API-first architecture |
| OAuth2 password flow | Better-Auth handles this; redundant implementation |

**Implementation Reference**: `.claude/skills/better-auth-config/SKILL.md`

---

### 2. SQLModel User-Task Relationship Pattern

**Decision**: Use UUID strings for `user_id` with foreign key constraint to user table.

**Rationale**:
- Better-Auth generates UUID-style identifiers for users
- SQLModel supports string-based foreign keys via `Field(foreign_key=...)`
- Query-level filtering by `user_id` enforces tenant isolation
- No ORM-level cascade needed; queries always scoped to authenticated user

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| Integer auto-increment user IDs | Conflicts with Better-Auth's UUID format |
| No foreign key constraint | Loses referential integrity |
| Row-level security (RLS) | PostgreSQL RLS adds complexity; app-level filtering sufficient |

---

### 3. Next.js App Router API Integration

**Decision**: Use server-side fetch with token injection for secure API calls.

**Rationale**:
- Next.js 16 App Router supports Server Components that can access session server-side
- API calls from server components can inject the JWT from the session
- Client-side calls use fetch with `Authorization` header from session context
- Avoids exposing tokens in client-side code unnecessarily

**Patterns**:
```typescript
// Server Component pattern
const session = await auth.api.getSession({ headers: await headers() });
const response = await fetch(`${API_URL}/tasks`, {
  headers: { Authorization: `Bearer ${session.token}` }
});

// Client Component pattern (via API route or direct)
const token = await getToken();
fetch('/api/proxy/tasks', { headers: { Authorization: `Bearer ${token}` } });
```

---

### 4. Neon PostgreSQL Connection Pooling

**Decision**: Use connection string with SQLModel's engine, relying on Neon's built-in pooling.

**Rationale**:
- Neon provides connection pooling at the edge by default
- SQLModel's create_engine with `pool_pre_ping=True` handles stale connections
- For serverless (Vercel), connection pooling prevents exhaustion
- No need for external pooler like PgBouncer

**Configuration**:
```python
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=True, pool_pre_ping=True)
```

---

### 5. Error Handling Strategy

**Decision**: Standardized error response format with sanitized messages.

**Rationale**:
- Consistent error structure simplifies frontend error handling
- Sanitized messages prevent information leakage (no stack traces in production)
- HTTP status codes follow REST conventions

**Error Response Schema**:
```json
{
  "detail": "Human-readable error message",
  "code": "ERROR_CODE",
  "status": 400
}
```

**Status Code Mapping**:
| Scenario | Status | Code |
|----------|--------|------|
| Invalid input | 400 | VALIDATION_ERROR |
| Not authenticated | 401 | UNAUTHORIZED |
| Not authorized | 403 | FORBIDDEN |
| Resource not found | 404 | NOT_FOUND |
| Server error | 500 | INTERNAL_ERROR |

---

### 6. Frontend State Management

**Decision**: React Query (TanStack Query) for server state, React Context for auth state.

**Rationale**:
- React Query handles caching, refetching, and optimistic updates
- Auth state (session, token) managed via Better-Auth's React hooks
- Minimal client-side state needed; server is source of truth

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| Redux | Overkill for task list CRUD |
| Zustand | Adds dependency when React Query suffices |
| SWR | React Query has better mutation support |

---

### 7. UI Component Strategy

**Decision**: Tailwind CSS with minimal component library (shadcn/ui patterns if needed).

**Rationale**:
- Constitution mandates Tailwind CSS
- Custom components keep bundle size small
- shadcn/ui provides accessible patterns without adding a dependency
- Mobile-first responsive design with Tailwind breakpoints

---

## Technology Verification

All technologies verified against constitution (`.specify/memory/constitution.md`):

| Requirement | Verified |
|-------------|----------|
| Next.js 16+ App Router | Planned |
| TypeScript strict mode | Planned |
| Tailwind CSS | Planned |
| FastAPI | Planned |
| SQLModel | Planned |
| Python 3.13+ | Planned |
| Neon PostgreSQL | Planned |
| Better Auth (frontend) | Planned |
| python-jose (backend) | Planned |

---

## Dependencies Identified

### Backend Dependencies (Python)
```txt
fastapi>=0.115.0
sqlmodel>=0.0.22
uvicorn[standard]>=0.32.0
python-jose[cryptography]>=3.3.0
python-dotenv>=1.0.0
psycopg2-binary>=2.9.0  # or asyncpg for async
pydantic>=2.0.0
pydantic-settings>=2.0.0
```

### Frontend Dependencies (Node.js)
```json
{
  "dependencies": {
    "next": "^16.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "better-auth": "^1.0.0",
    "@tanstack/react-query": "^5.0.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "@types/node": "^22.0.0",
    "@types/react": "^19.0.0",
    "tailwindcss": "^4.0.0",
    "postcss": "^8.0.0"
  }
}
```

---

## Unknowns Resolved

| Original Unknown | Resolution |
|------------------|------------|
| JWT algorithm | HS256 with shared secret |
| User ID format | UUID string from Better-Auth `sub` claim |
| Connection pooling | Neon built-in pooling |
| State management | React Query for server state |
| Error format | Standardized JSON with detail/code/status |

---

## Research Complete

All technical decisions documented. Proceeding to Phase 1: Design & Contracts.
