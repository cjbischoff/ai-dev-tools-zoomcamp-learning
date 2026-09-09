"""FastAPI dependency injection."""

import hashlib
from typing import Optional

from fastapi import Cookie, Depends, HTTPException, status

from app.database import MockDatabaseService, User


# --- Global database service ---
# Swapped for SQLAlchemy in Q6.
_db = MockDatabaseService()


def get_db() -> MockDatabaseService:
    """Dependency: returns the shared DB service."""
    return _db


def set_db(db: MockDatabaseService) -> None:
    """Replace the DB service (used for testing or Q6 swap)."""
    global _db
    _db = db


# --- Password helpers ---

def hash_password(password: str) -> str:
    """Simple SHA-256 hash. FIXME: use bcrypt/argon2 in production."""
    return hashlib.sha256(password.encode()).hexdigest()


# --- Auth dependency ---

async def get_current_user(
    kanvas_session: Optional[str] = Cookie(None),
    db: MockDatabaseService = Depends(get_db),
) -> User:
    """Extract the authenticated user from the session cookie."""
    if not kanvas_session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    user = db.get_user_by_token(kanvas_session)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")
    return user
