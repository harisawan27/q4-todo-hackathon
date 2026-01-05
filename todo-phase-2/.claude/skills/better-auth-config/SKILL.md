# Better Auth Configuration Skill

## Overview

This skill defines the authentication handshake between the Next.js frontend (using Better-Auth) and the FastAPI backend for the Phase II multi-user web application.

## Technical Stack

| Layer    | Technology                     |
|----------|--------------------------------|
| Frontend | Next.js 16 (App Router), TypeScript |
| Backend  | FastAPI, SQLModel              |
| Database | Neon PostgreSQL                |
| Auth     | Better-Auth (frontend), python-jose (backend) |

---

## 1. Better-Auth JWT Configuration (Frontend)

Better-Auth issues JWTs via the `jwt` plugin using a shared secret.

### Environment Variable

```env
BETTER_AUTH_SECRET=<your-shared-secret>
```

### Better-Auth Setup

```typescript
// lib/auth.ts
import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";

export const auth = betterAuth({
  // ... other config
  plugins: [
    jwt({
      jwt: {
        expirationTime: "7d",
      },
    }),
  ],
  secret: process.env.BETTER_AUTH_SECRET,
});
```

### Token Structure

The JWT payload includes:

```json
{
  "sub": "<user_id>",
  "email": "<user_email>",
  "iat": 1234567890,
  "exp": 1234567890
}
```

The `sub` claim is the **canonical user identifier** used across all systems.

---

## 2. FastAPI JWT Verification (Backend)

The backend verifies incoming JWTs using `python-jose` with the same shared secret.

### Environment Variable

```env
BETTER_AUTH_SECRET=<your-shared-secret>
```

### Dependencies

```bash
pip install python-jose[cryptography]
```

### JWT Bearer Dependency

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
    """
    Verify JWT from Authorization: Bearer <token> header.
    Returns TokenData with user_id (sub claim) on success.
    Raises 401 on invalid/expired token.
    """
    token = credentials.credentials
    secret = os.getenv("BETTER_AUTH_SECRET")

    if not secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Auth secret not configured"
        )

    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=["HS256"]
        )
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

### Header Format

```
Authorization: Bearer <jwt_token>
```

---

## 3. SQLModel Query Enforcement Rule

**MANDATORY**: All SQLModel queries MUST filter by the `sub` claim (`user_id`) from the JWT to ensure tenant isolation.

### Correct Pattern

```python
# app/routes/todos.py
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.auth.jwt_bearer import get_current_user, TokenData
from app.models import Todo
from app.database import get_session

router = APIRouter()

@router.get("/todos")
def get_todos(
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # CORRECT: Filter by user_id from JWT
    statement = select(Todo).where(Todo.user_id == current_user.user_id)
    todos = session.exec(statement).all()
    return todos

@router.get("/todos/{todo_id}")
def get_todo(
    todo_id: int,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # CORRECT: Always include user_id filter
    statement = select(Todo).where(
        Todo.id == todo_id,
        Todo.user_id == current_user.user_id
    )
    todo = session.exec(statement).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo
```

### Forbidden Pattern

```python
# WRONG: Missing user_id filter - SECURITY VULNERABILITY
@router.get("/todos/{todo_id}")
def get_todo_INSECURE(todo_id: int, session: Session = Depends(get_session)):
    statement = select(Todo).where(Todo.id == todo_id)  # NO USER FILTER!
    return session.exec(statement).first()
```

---

## 4. Validation Checklist

Before any route is approved:

- [ ] Route has `Depends(get_current_user)` dependency
- [ ] All SQLModel queries include `.where(...user_id == current_user.user_id)`
- [ ] No raw SQL without user_id parameterization
- [ ] Frontend sends `Authorization: Bearer <token>` header
- [ ] Both frontend and backend use identical `BETTER_AUTH_SECRET`

---

## 5. Secret Synchronization

The shared secret MUST be identical in both environments:

| Environment | Variable Name        | Location          |
|-------------|---------------------|-------------------|
| Frontend    | `BETTER_AUTH_SECRET` | `.env.local`      |
| Backend     | `BETTER_AUTH_SECRET` | `.env` or secrets |

**Never commit secrets to version control.** Use environment variables or a secrets manager.
