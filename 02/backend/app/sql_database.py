"""
SQLAlchemy-based database service.

Implements the same interface as MockDatabaseService using SQLite.
Swap with MockDatabaseService in dependencies.py to toggle.
"""

from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Board, BoardMember, Card, Session, User
from app.models import Base, BoardMemberModel, BoardModel, CardModel, SessionModel, UserModel


class SqlDatabaseService:
    """Database service backed by SQLAlchemy + SQLite."""

    def __init__(self, db_url: str = "sqlite:///kanvas.db"):
        connect_args = {"check_same_thread": False}
        if db_url == "sqlite:///:memory:":
            self.engine = create_engine(
                db_url, poolclass=StaticPool, connect_args=connect_args
            )
        else:
            self.engine = create_engine(db_url, connect_args=connect_args)
        Base.metadata.create_all(self.engine)
        self._session_factory = sessionmaker(bind=self.engine)

    # ------------------------------------------------------------------
    # Session helpers
    # ------------------------------------------------------------------

    @contextmanager
    def _session(self):
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _token(self) -> str:
        return uuid4().hex

    @staticmethod
    def _user_from(m) -> User:
        return User(id=m.id, username=m.username, password_hash=m.password_hash)

    @staticmethod
    def _session_from(m) -> Session:
        return Session(id=m.id, user_id=m.user_id, token=m.token, created_at=m.created_at)

    @staticmethod
    def _board_from(m) -> Board:
        return Board(id=m.id, name=m.name, owner_id=m.owner_id, created_at=m.created_at)

    @staticmethod
    def _member_from(m) -> BoardMember:
        return BoardMember(id=m.id, board_id=m.board_id, user_id=m.user_id, role=m.role)

    @staticmethod
    def _card_from(m) -> Card:
        return Card(
            id=m.id,
            board_id=m.board_id,
            column=m.column,
            title=m.title,
            description=m.description,
            due_date=m.due_date,
            assignee=m.assignee,
            position=m.position,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )

    # ------------------------------------------------------------------
    # Users
    # ------------------------------------------------------------------

    def create_user(self, username: str, password_hash: str) -> User:
        with self._session() as s:
            model = UserModel(username=username, password_hash=password_hash)
            s.add(model)
            s.flush()
            return self._user_from(model)

    def get_user_by_username(self, username: str) -> Optional[User]:
        with self._session() as s:
            model = s.query(UserModel).filter_by(username=username).first()
            return self._user_from(model) if model else None

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        with self._session() as s:
            model = s.query(UserModel).filter_by(id=user_id).first()
            return self._user_from(model) if model else None

    # ------------------------------------------------------------------
    # Sessions
    # ------------------------------------------------------------------

    def create_session(self, user_id: int) -> Session:
        with self._session() as s:
            model = SessionModel(
                user_id=user_id,
                token=self._token(),
                created_at=self._now(),
            )
            s.add(model)
            s.flush()
            return self._session_from(model)

    def get_session_by_token(self, token: str) -> Optional[Session]:
        with self._session() as s:
            model = s.query(SessionModel).filter_by(token=token).first()
            return self._session_from(model) if model else None

    def delete_session(self, token: str) -> None:
        with self._session() as s:
            s.query(SessionModel).filter_by(token=token).delete()

    def get_user_by_token(self, token: str) -> Optional[User]:
        with self._session() as s:
            sess = s.query(SessionModel).filter_by(token=token).first()
            if sess is None:
                return None
            user = s.query(UserModel).filter_by(id=sess.user_id).first()
            return self._user_from(user) if user else None

    # ------------------------------------------------------------------
    # Boards
    # ------------------------------------------------------------------

    def create_board(self, name: str, owner_id: int) -> Board:
        with self._session() as s:
            model = BoardModel(name=name, owner_id=owner_id, created_at=self._now())
            s.add(model)
            s.flush()
            # Auto-add owner as member
            member = BoardMemberModel(board_id=model.id, user_id=owner_id, role="owner")
            s.add(member)
            s.flush()
            return self._board_from(model)

    def get_board(self, board_id: int) -> Optional[Board]:
        with self._session() as s:
            model = s.query(BoardModel).filter_by(id=board_id).first()
            return self._board_from(model) if model else None

    def get_boards_for_user(self, user_id: int) -> list[Board]:
        with self._session() as s:
            board_ids = [
                r[0]
                for r in s.query(BoardMemberModel.board_id)
                .filter_by(user_id=user_id)
                .all()
            ]
            if not board_ids:
                return []
            models = s.query(BoardModel).filter(BoardModel.id.in_(board_ids)).all()
            return [self._board_from(m) for m in models]

    def update_board(self, board_id: int, name: str) -> Optional[Board]:
        with self._session() as s:
            model = s.query(BoardModel).filter_by(id=board_id).first()
            if model is None:
                return None
            model.name = name
            s.flush()
            return self._board_from(model)

    def delete_board(self, board_id: int) -> bool:
        with self._session() as s:
            model = s.query(BoardModel).filter_by(id=board_id).first()
            if model is None:
                return False
            s.delete(model)
            s.query(BoardMemberModel).filter_by(board_id=board_id).delete()
            s.query(CardModel).filter_by(board_id=board_id).delete()
            return True

    def get_members(self, board_id: int) -> list[BoardMember]:
        with self._session() as s:
            models = (
                s.query(BoardMemberModel).filter_by(board_id=board_id).all()
            )
            return [self._member_from(m) for m in models]

    def is_member(self, board_id: int, user_id: int) -> bool:
        with self._session() as s:
            return (
                s.query(BoardMemberModel)
                .filter_by(board_id=board_id, user_id=user_id)
                .first()
                is not None
            )

    def add_member(self, board_id: int, user_id: int, role: str = "member") -> BoardMember:
        with self._session() as s:
            model = BoardMemberModel(board_id=board_id, user_id=user_id, role=role)
            s.add(model)
            s.flush()
            return self._member_from(model)

    def remove_member(self, board_id: int, user_id: int) -> bool:
        with self._session() as s:
            deleted = (
                s.query(BoardMemberModel)
                .filter_by(board_id=board_id, user_id=user_id)
                .delete()
            )
            return deleted > 0

    # ------------------------------------------------------------------
    # Cards
    # ------------------------------------------------------------------

    def create_card(
        self,
        board_id: int,
        column: str,
        title: str,
        description: str = "",
        due_date: str = "",
        assignee: str = "",
    ) -> Card:
        with self._session() as s:
            max_pos = (
                s.query(CardModel.position)
                .filter_by(board_id=board_id, column=column)
                .order_by(CardModel.position.desc())
                .first()
            )
            pos = (max_pos[0] if max_pos else 0) + 1
            now = self._now()
            model = CardModel(
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
            s.add(model)
            s.flush()
            return self._card_from(model)

    def get_card(self, card_id: int) -> Optional[Card]:
        with self._session() as s:
            model = s.query(CardModel).filter_by(id=card_id).first()
            return self._card_from(model) if model else None

    def get_cards_for_board(self, board_id: int) -> list[Card]:
        with self._session() as s:
            models = (
                s.query(CardModel)
                .filter_by(board_id=board_id)
                .order_by(CardModel.position)
                .all()
            )
            return [self._card_from(m) for m in models]

    def update_card(self, card_id: int, fields: dict) -> Optional[Card]:
        with self._session() as s:
            model = s.query(CardModel).filter_by(id=card_id).first()
            if model is None:
                return None
            for key in ("title", "description", "due_date", "assignee"):
                if key in fields:
                    setattr(model, key, fields[key])
            model.updated_at = self._now()
            s.flush()
            return self._card_from(model)

    def delete_card(self, card_id: int) -> bool:
        with self._session() as s:
            deleted = s.query(CardModel).filter_by(id=card_id).delete()
            return deleted > 0

    def move_card(self, card_id: int, new_column: str, new_position: int) -> Optional[Card]:
        with self._session() as s:
            model = s.query(CardModel).filter_by(id=card_id).first()
            if model is None:
                return None
            model.column = new_column
            model.updated_at = self._now()
            s.flush()

            # Renumber all cards in the target column
            col_cards = (
                s.query(CardModel)
                .filter_by(board_id=model.board_id, column=new_column)
                .order_by(CardModel.position)
                .all()
            )
            # Remove the moved card from the list, insert at new position
            ordered = [c for c in col_cards if c.id != card_id]
            ordered.insert(new_position - 1, model)
            for i, c in enumerate(ordered):
                c.position = i + 1
            s.flush()
            return self._card_from(model)

    def reorder_cards(self, board_id: int, column: str, card_ids: list[int]) -> bool:
        with self._session() as s:
            models = (
                s.query(CardModel)
                .filter_by(board_id=board_id, column=column)
                .all()
            )
            ids_set = set(card_ids)
            if not all(c.id in ids_set for c in models):
                return False
            for i, cid in enumerate(card_ids):
                model = s.query(CardModel).filter_by(id=cid).first()
                if model:
                    model.position = i + 1
            return True
