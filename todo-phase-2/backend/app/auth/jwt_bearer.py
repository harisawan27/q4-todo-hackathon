"""JWT verification dependency for FastAPI using PyJWT with JWKS"""

import json
from dataclasses import dataclass

import jwt
from jwt import PyJWK
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, text

from app.database import engine

# Security scheme for JWT Bearer tokens
security = HTTPBearer()


@dataclass
class CurrentUser:
    """Represents the authenticated user from JWT"""

    user_id: str


def get_jwks_public_key(kid: str) -> dict | None:
    """Fetch public key from JWKS table by key ID"""
    with Session(engine) as session:
        result = session.exec(
            text('SELECT "publicKey" FROM jwks WHERE id = :kid'),
            params={"kid": kid}
        )
        row = result.first()
        if row:
            return json.loads(row[0])
    return None


def verify_token(token: str) -> CurrentUser:
    """Verify JWT token and extract user_id from sub claim"""
    try:
        # Decode header to get key ID
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        alg = unverified_header.get("alg", "EdDSA")

        if not kid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing key ID",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Fetch public key from JWKS
        jwk_data = get_jwks_public_key(kid)
        if not jwk_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: unknown signing key",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Construct PyJWK from the JWK data
        jwk_data["kid"] = kid
        jwk_obj = PyJWK.from_dict(jwk_data)

        # Verify and decode token
        payload = jwt.decode(
            token,
            jwk_obj.key,
            algorithms=[alg],
            options={"verify_aud": False},
        )

        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user identifier",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return CurrentUser(user_id=user_id)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> CurrentUser:
    """FastAPI dependency that returns the authenticated user or raises 401"""
    return verify_token(credentials.credentials)
