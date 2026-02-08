"""JWT Bearer authentication middleware for FastAPI."""

import logging
import os
from typing import Optional

import httpx
import jwt
from jwt import PyJWK, PyJWKClient
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

logger = logging.getLogger("chat-api")

security = HTTPBearer(auto_error=False)

_jwks_client: Optional[PyJWKClient] = None


def _get_jwks_client() -> PyJWKClient:
    global _jwks_client
    if _jwks_client is None:
        auth_url = os.environ.get("AUTH_JWKS_URL", "http://frontend:3000/api/auth/jwks")
        _jwks_client = PyJWKClient(auth_url, cache_keys=True, lifespan=3600)
    return _jwks_client


async def get_current_user(request: Request) -> str:
    """Extract and validate user_id from JWT token."""
    credentials: Optional[HTTPAuthorizationCredentials] = await security(request)
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "UNAUTHORIZED", "message": "Missing authentication token"},
        )

    try:
        client = _get_jwks_client()
        signing_key = client.get_signing_key_from_jwt(credentials.credentials)
        payload = jwt.decode(
            credentials.credentials,
            signing_key.key,
            algorithms=["EdDSA", "HS256"],
            options={"verify_aud": False},
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": "UNAUTHORIZED", "message": "Invalid token: missing sub claim"},
            )
        return user_id
    except jwt.exceptions.PyJWTError as e:
        logger.warning(f"JWT validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "UNAUTHORIZED", "message": "Invalid or expired token"},
        )
