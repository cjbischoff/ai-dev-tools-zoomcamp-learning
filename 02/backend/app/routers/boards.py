"""Board endpoints: CRUD, members."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.database import MockDatabaseService
from app.dependencies import get_current_user, get_db
from app.schemas import (
    BoardDetailOut,
    BoardOut,
    BoardSummaryOut,
    CreateBoardRequest,
    InviteMemberRequest,
    MemberOut,
    RenameBoardRequest,
    SuccessResponse,
    UserOut,
)
from app.database import User

router = APIRouter(prefix="/api/boards", tags=["Boards"])


def _require_board_access(board_id: int, user: User, db: MockDatabaseService):
    """Return the board if the user is a member, else raise 403/404."""
    board = db.get_board(board_id)
    if board is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
    if not db.is_member(board_id, user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a board member")
    return board


def _require_owner(board_id: int, user: User, db: MockDatabaseService):
    """Return the board if the user is the owner, else raise 403."""
    board = _require_board_access(board_id, user, db)
    if board.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the owner can perform this action")
    return board


@router.get("", response_model=list[BoardSummaryOut])
def list_boards(user: User = Depends(get_current_user), db: MockDatabaseService = Depends(get_db)):
    boards = db.get_boards_for_user(user.id)
    result = []
    for b in boards:
        members = db.get_members(b.id)
        result.append(BoardSummaryOut(
            id=b.id,
            name=b.name,
            owner_id=b.owner_id,
            created_at=b.created_at,
            member_count=len(members),
            is_owner=b.owner_id == user.id,
        ))
    return result


@router.post("", response_model=BoardOut, status_code=status.HTTP_201_CREATED)
def create_board(
    body: CreateBoardRequest,
    user: User = Depends(get_current_user),
    db: MockDatabaseService = Depends(get_db),
):
    board = db.create_board(body.name, user.id)
    return BoardOut(id=board.id, name=board.name, owner_id=board.owner_id, created_at=board.created_at)


@router.get("/{board_id}", response_model=BoardDetailOut)
def get_board_detail(
    board_id: int,
    user: User = Depends(get_current_user),
    db: MockDatabaseService = Depends(get_db),
):
    board = _require_board_access(board_id, user, db)

    members = db.get_members(board_id)
    member_out = []
    for m in members:
        u = db.get_user_by_id(m.user_id)
        member_out.append(MemberOut(
            user_id=m.user_id,
            username=u.username if u else "unknown",
            role=m.role,
        ))

    cards = db.get_cards_for_board(board_id)
    cards_out = [
        {
            "id": c.id,
            "board_id": c.board_id,
            "column": c.column,
            "title": c.title,
            "description": c.description,
            "due_date": c.due_date,
            "assignee": c.assignee,
            "position": c.position,
            "created_at": c.created_at,
            "updated_at": c.updated_at,
        }
        for c in sorted(cards, key=lambda c: c.position)
    ]

    return BoardDetailOut(
        id=board.id,
        name=board.name,
        owner_id=board.owner_id,
        created_at=board.created_at,
        members=member_out,
        cards=cards_out,
    )


@router.put("/{board_id}", response_model=BoardOut)
def rename_board(
    board_id: int,
    body: RenameBoardRequest,
    user: User = Depends(get_current_user),
    db: MockDatabaseService = Depends(get_db),
):
    board = _require_board_access(board_id, user, db)
    updated = db.update_board(board_id, body.name)
    return BoardOut(id=updated.id, name=updated.name, owner_id=updated.owner_id, created_at=updated.created_at)


@router.delete("/{board_id}", response_model=SuccessResponse)
def delete_board(
    board_id: int,
    user: User = Depends(get_current_user),
    db: MockDatabaseService = Depends(get_db),
):
    _require_owner(board_id, user, db)
    db.delete_board(board_id)
    return SuccessResponse(success=True)


# --- Members ---

@router.post("/{board_id}/members", response_model=SuccessResponse)
def invite_member(
    board_id: int,
    body: InviteMemberRequest,
    user: User = Depends(get_current_user),
    db: MockDatabaseService = Depends(get_db),
):
    _require_owner(board_id, user, db)
    target = db.get_user_by_username(body.username)
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if db.is_member(board_id, target.id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User is already a member")
    db.add_member(board_id, target.id, role="member")
    return SuccessResponse(success=True)


@router.delete("/{board_id}/members/{user_id}", response_model=SuccessResponse)
def remove_member(
    board_id: int,
    user_id: int,
    user: User = Depends(get_current_user),
    db: MockDatabaseService = Depends(get_db),
):
    _require_owner(board_id, user, db)
    if user_id == user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove the owner")
    db.remove_member(board_id, user_id)
    return SuccessResponse(success=True)
