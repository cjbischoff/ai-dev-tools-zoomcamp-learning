"""
Mock database service — in-memory store.

Swap this module's implementation for SQLAlchemy in Q6 without changing
any router code (they depend on the same method signatures via DI).
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class User:
    id: int
    username: str
    password_hash: str  # FIXME: use proper hashing in production


@dataclass
class Session:
    id: int
    user_id: int
    token: str
    created_at: str


@dataclass
class Board:
    id: int
    name: str
    owner_id: int
    created_at: str


@dataclass
class BoardMember:
    id: int
    board_id: int
    user_id: int
    role: str  # "owner" | "member"


@dataclass
class Card:
    id: int
    board_id: int
    column: str  # "todo" | "in_progress" | "done"
    title: str
    description: str
    due_date: str  # "" or "YYYY-MM-DD"
    assignee: str
    position: int
    created_at: str
    updated_at: str


# ---------------------------------------------------------------------------
# Mock database service
# ---------------------------------------------------------------------------

class MockDatabaseService:
    """In-memory store with auto-incrementing IDs."""

    def __init__(self):
        self._reset()

    def _reset(self):
        self._next_id = 1
        self._users: dict[int, User] = {}
        self._sessions: dict[str, Session] = {}  # token -> Session
        self._boards: dict[int, Board] = {}
        self._members: list[BoardMember] = []
        self._cards: dict[int, Card] = {}

    # -- helpers --

    def _uid(self) -> int:
        n = self._next_id
        self._next_id += 1
        return n

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _token(self) -> str:
        return uuid.uuid4().hex

    def _board_ids_for_user(self, user_id: int) -> set[int]:
        return {
            m.board_id for m in self._members
            if m.user_id == user_id
        }

    # -- users --

    def create_user(self, username: str, password_hash: str) -> User:
        user = User(id=self._uid(), username=username, password_hash=password_hash)
        self._users[user.id] = user
        return user

    def get_user_by_username(self, username: str) -> Optional[User]:
        for u in self._users.values():
            if u.username == username:
                return u
        return None

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self._users.get(user_id)

    # -- sessions --

    def create_session(self, user_id: int) -> Session:
        token = self._token()
        sess = Session(
            id=self._uid(),
            user_id=user_id,
            token=token,
            created_at=self._now(),
        )
        self._sessions[token] = sess
        return sess

    def get_session_by_token(self, token: str) -> Optional[Session]:
        return self._sessions.get(token)

    def delete_session(self, token: str) -> None:
        self._sessions.pop(token, None)

    def get_user_by_token(self, token: str) -> Optional[User]:
        sess = self._sessions.get(token)
        if sess is None:
            return None
        return self._users.get(sess.user_id)

    # -- boards --

    def create_board(self, name: str, owner_id: int) -> Board:
        board = Board(
            id=self._uid(),
            name=name,
            owner_id=owner_id,
            created_at=self._now(),
        )
        self._boards[board.id] = board
        # Owner is automatically a member
        self._members.append(BoardMember(
            id=self._uid(), board_id=board.id, user_id=owner_id, role="owner",
        ))
        return board

    def get_board(self, board_id: int) -> Optional[Board]:
        return self._boards.get(board_id)

    def get_boards_for_user(self, user_id: int) -> list[Board]:
        ids = self._board_ids_for_user(user_id)
        return [self._boards[b] for b in ids if b in self._boards]

    def update_board(self, board_id: int, name: str) -> Optional[Board]:
        board = self._boards.get(board_id)
        if board is None:
            return None
        board.name = name
        return board

    def delete_board(self, board_id: int) -> bool:
        if board_id not in self._boards:
            return False
        del self._boards[board_id]
        self._members = [m for m in self._members if m.board_id != board_id]
        self._cards = {k: v for k, v in self._cards.items() if v.board_id != board_id}
        return True

    def get_members(self, board_id: int) -> list[BoardMember]:
        return [m for m in self._members if m.board_id == board_id]

    def is_member(self, board_id: int, user_id: int) -> bool:
        return any(
            m.board_id == board_id and m.user_id == user_id
            for m in self._members
        )

    def add_member(self, board_id: int, user_id: int, role: str = "member") -> BoardMember:
        m = BoardMember(id=self._uid(), board_id=board_id, user_id=user_id, role=role)
        self._members.append(m)
        return m

    def remove_member(self, board_id: int, user_id: int) -> bool:
        before = len(self._members)
        self._members = [
            m for m in self._members
            if not (m.board_id == board_id and m.user_id == user_id)
        ]
        return len(self._members) < before

    # -- cards --

    def create_card(
        self,
        board_id: int,
        column: str,
        title: str,
        description: str = "",
        due_date: str = "",
        assignee: str = "",
    ) -> Card:
        # Position = max + 1 in the same column
        col_cards = [
            c for c in self._cards.values()
            if c.board_id == board_id and c.column == column
        ]
        pos = max((c.position for c in col_cards), default=0) + 1
        now = self._now()
        card = Card(
            id=self._uid(),
            board_id=board_id,
            column=column,
            title=title,
            description=description,
            due_date=due_date,
            assignee=assignee,
            position=pos,
            created_at=now,
            updated_at=now,
        )
        self._cards[card.id] = card
        return card

    def get_card(self, card_id: int) -> Optional[Card]:
        return self._cards.get(card_id)

    def get_cards_for_board(self, board_id: int) -> list[Card]:
        return [c for c in self._cards.values() if c.board_id == board_id]

    def update_card(self, card_id: int, fields: dict) -> Optional[Card]:
        card = self._cards.get(card_id)
        if card is None:
            return None
        for key in ("title", "description", "due_date", "assignee"):
            if key in fields:
                setattr(card, key, fields[key])
        card.updated_at = self._now()
        return card

    def delete_card(self, card_id: int) -> bool:
        if card_id not in self._cards:
            return False
        board_id = self._cards[card_id].board_id
        del self._cards[card_id]
        return True

    def move_card(self, card_id: int, new_column: str, new_position: int) -> Optional[Card]:
        card = self._cards.get(card_id)
        if card is None:
            return None
        card.column = new_column
        card.updated_at = self._now()

        # Re-number positions in target column
        col_cards = sorted(
            [c for c in self._cards.values() if c.board_id == card.board_id and c.column == new_column and c.id != card_id],
            key=lambda c: c.position,
        )
        col_cards.insert(new_position - 1, card)
        for i, c in enumerate(col_cards):
            c.position = i + 1
        return card

    def reorder_cards(self, board_id: int, column: str, card_ids: list[int]) -> bool:
        col_cards = [
            c for c in self._cards.values()
            if c.board_id == board_id and c.column == column
        ]
        ids_set = set(card_ids)
        if not all(c.id in ids_set for c in col_cards):
            return False
        for c in col_cards:
            if c.id not in ids_set:
                return False
        for i, cid in enumerate(card_ids):
            if cid in self._cards:
                self._cards[cid].position = i + 1
        return True
