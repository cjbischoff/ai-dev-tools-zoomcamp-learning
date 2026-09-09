"""Kanvas FastAPI application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import MockDatabaseService
from app.dependencies import get_db
from app.routers import auth, boards, cards


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Seed demo data on startup, nothing special on shutdown."""
    db = get_db()
    _seed_demo_data(db)
    yield


def _seed_demo_data(db: MockDatabaseService):
    """Add initial users, boards, and cards for development."""
    # Users
    from app.dependencies import hash_password
    alice = db.create_user("alice", hash_password("pass123"))
    bob = db.create_user("bob", hash_password("pass123"))

    # Boards
    sprint24 = db.create_board("Sprint 24", alice.id)
    ideas = db.create_board("Ideas", alice.id)

    # Members
    db.add_member(sprint24.id, bob.id, role="member")

    # Cards on Sprint 24
    db.create_card(sprint24.id, "todo", "Design landing page",
                   "Create mockups for the new landing page", "2026-09-20")
    db.create_card(sprint24.id, "todo", "Set up CI pipeline",
                   "", "", "bob")
    db.create_card(sprint24.id, "in_progress", "API rate limiting",
                   "Add rate limiting middleware", "2026-09-05")
    db.create_card(sprint24.id, "in_progress", "User dashboard",
                   "Build the user dashboard", "2026-09-15", "alice")
    db.create_card(sprint24.id, "done", "User authentication",
                   "Implement login and registration", "2026-09-05")

    # Cards on Ideas
    db.create_card(ideas.id, "todo", "Read about AI agents")


app = FastAPI(
    title="Kanvas API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(boards.router)
app.include_router(cards.router)
