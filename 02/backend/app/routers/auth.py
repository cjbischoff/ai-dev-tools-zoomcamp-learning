"""Auth endpoints: register, login, logout, me."""

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.database import MockDatabaseService
from app.dependencies import get_current_user, get_db, hash_password
from app.schemas import AuthLoginRequest, AuthRegisterRequest, AuthResponse, UserOut

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/register", response_model=AuthResponse)
def register(body: AuthRegisterRequest, response: Response, db: MockDatabaseService = Depends(get_db)):
    if db.get_user_by_username(body.username):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")
    user = db.create_user(body.username, hash_password(body.password))
    sess = db.create_session(user.id)
    response.set_cookie(key="kanvas_session", value=sess.token, httponly=True, samesite="lax")
    return {"user": UserOut(id=user.id, username=user.username)}


@router.post("/login", response_model=AuthResponse)
def login(body: AuthLoginRequest, response: Response, db: MockDatabaseService = Depends(get_db)):
    user = db.get_user_by_username(body.username)
    if not user or user.password_hash != hash_password(body.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    sess = db.create_session(user.id)
    response.set_cookie(key="kanvas_session", value=sess.token, httponly=True, samesite="lax")
    return {"user": UserOut(id=user.id, username=user.username)}


@router.post("/logout")
def logout(response: Response, db: MockDatabaseService = Depends(get_db), user=Depends(get_current_user)):
    # Best-effort: clear cookie even if session lookup fails
    response.delete_cookie("kanvas_session")
    return {"success": True}


@router.get("/me", response_model=AuthResponse)
def me(user=Depends(get_current_user)):
    return {"user": UserOut(id=user.id, username=user.username)}
