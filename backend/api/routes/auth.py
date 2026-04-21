"""
Authentication routes: register, login, and profile update.
"""

from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional

from backend.database import get_db, User
from backend.utils.auth_utils import hash_password, verify_password, create_access_token, decode_token

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    city: Optional[str] = None
    age_group: Optional[str] = None
    health_condition: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ProfileUpdateRequest(BaseModel):
    full_name: str
    city: Optional[str] = None
    age_group: Optional[str] = None
    health_condition: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    city: Optional[str]
    age_group: Optional[str]
    health_condition: Optional[str]

    class Config:
        from_attributes = True


# ── Register ──────────────────────────────────────────────────────────────────
@router.post("/register", status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    user = User(
        full_name=payload.full_name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        city=payload.city,
        age_group=payload.age_group,
        health_condition=payload.health_condition,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.email, "user_id": user.id})
    return {"access_token": token, "token_type": "bearer", "user": UserResponse.from_orm(user)}


# ── Login ─────────────────────────────────────────────────────────────────────
@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    token = create_access_token({"sub": user.email, "user_id": user.id})
    return {"access_token": token, "token_type": "bearer", "user": UserResponse.from_orm(user)}


# ── Update Profile ────────────────────────────────────────────────────────────
@router.put("/profile")
def update_profile(
    payload: ProfileUpdateRequest,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(default=None)
):
    """Update logged-in user's profile. Requires Authorization: Bearer <token>"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated.")

    token = authorization.split(" ", 1)[1]
    data = decode_token(token)
    if not data:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")

    user = db.query(User).filter(User.email == data["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    user.full_name = payload.full_name
    user.city = payload.city
    user.age_group = payload.age_group
    user.health_condition = payload.health_condition
    db.commit()
    db.refresh(user)

    return {"message": "Profile updated successfully.", "user": UserResponse.from_orm(user)}