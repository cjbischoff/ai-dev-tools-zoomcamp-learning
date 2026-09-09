"""SQLAlchemy ORM models for the Kanvas database."""

from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)


class SessionModel(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    token = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(String(50), nullable=False)


class BoardModel(Base):
    __tablename__ = "boards"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    owner_id = Column(Integer, nullable=False)
    created_at = Column(String(50), nullable=False)


class BoardMemberModel(Base):
    __tablename__ = "board_members"

    id = Column(Integer, primary_key=True)
    board_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    role = Column(String(20), nullable=False)


class CardModel(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True)
    board_id = Column(Integer, nullable=False)
    column = Column(String(20), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(String, default="")
    due_date = Column(String(20), default="")
    assignee = Column(String(100), default="")
    position = Column(Integer, nullable=False)
    created_at = Column(String(50), nullable=False)
    updated_at = Column(String(50), nullable=False)
