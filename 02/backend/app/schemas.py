"""Pydantic request/response models for the Kanvas API."""

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class AuthRegisterRequest(BaseModel):
    username: str = Field(min_length=3)
    password: str = Field(min_length=6)


class AuthLoginRequest(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str


class AuthResponse(BaseModel):
    user: UserOut


# ---------------------------------------------------------------------------
# Boards
# ---------------------------------------------------------------------------

class CreateBoardRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class RenameBoardRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class BoardOut(BaseModel):
    id: int
    name: str
    owner_id: int
    created_at: str


class BoardSummaryOut(BoardOut):
    member_count: int
    is_owner: bool


class MemberOut(BaseModel):
    user_id: int
    username: str
    role: str


class CardOut(BaseModel):
    id: int
    board_id: int
    column: str
    title: str
    description: str
    due_date: str
    assignee: str
    position: int
    created_at: str
    updated_at: str


class BoardDetailOut(BoardOut):
    members: list[MemberOut]
    cards: list[CardOut]


class InviteMemberRequest(BaseModel):
    username: str


# ---------------------------------------------------------------------------
# Cards
# ---------------------------------------------------------------------------

class CreateCardRequest(BaseModel):
    column: str = Field(pattern=r"^(todo|in_progress|done)$")
    title: str = Field(min_length=1, max_length=200)
    description: str = ""
    due_date: str = ""
    assignee: str = ""


class UpdateCardRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    due_date: Optional[str] = None
    assignee: Optional[str] = None


class MoveCardRequest(BaseModel):
    new_column: str = Field(pattern=r"^(todo|in_progress|done)$")
    new_position: int = Field(ge=1)


class ReorderRequest(BaseModel):
    column: str = Field(pattern=r"^(todo|in_progress|done)$")
    card_ids: list[int]


# ---------------------------------------------------------------------------
# Generic
# ---------------------------------------------------------------------------

class SuccessResponse(BaseModel):
    success: bool
