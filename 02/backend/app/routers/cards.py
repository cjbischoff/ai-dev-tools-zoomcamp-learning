"""Card endpoints: CRUD, move, reorder."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.database import MockDatabaseService
from app.dependencies import get_current_user, get_db
from app.schemas import (
    CardOut,
    CreateCardRequest,
    MoveCardRequest,
    ReorderRequest,
    SuccessResponse,
    UpdateCardRequest,
)
from app.database import User

router = APIRouter(tags=["Cards"])


def _require_board_access(board_id: int, user: User, db: MockDatabaseService):
    """Return the board if the user is a member, else raise 403/404."""
    board = db.get_board(board_id)
    if board is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
    if not db.is_member(board_id, user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a board member")
    return board


def _card_to_out(card) -> CardOut:
    return CardOut(
        id=card.id,
        board_id=card.board_id,
        column=card.column,
        title=card.title,
        description=card.description,
        due_date=card.due_date,
        assignee=card.assignee,
        position=card.position,
        created_at=card.created_at,
        updated_at=card.updated_at,
    )


# Cards are nested under boards for creation, but have their own resource paths for update/delete/move


@router.post("/api/boards/{board_id}/cards", response_model=CardOut, status_code=status.HTTP_201_CREATED)
def create_card(
    board_id: int,
    body: CreateCardRequest,
    user: User = Depends(get_current_user),
    db: MockDatabaseService = Depends(get_db),
):
    _require_board_access(board_id, user, db)
    card = db.create_card(
        board_id=board_id,
        column=body.column,
        title=body.title,
        description=body.description,
        due_date=body.due_date,
        assignee=body.assignee,
    )
    return _card_to_out(card)


@router.put("/api/cards/{card_id}", response_model=CardOut)
def update_card(
    card_id: int,
    body: UpdateCardRequest,
    user: User = Depends(get_current_user),
    db: MockDatabaseService = Depends(get_db),
):
    card = db.get_card(card_id)
    if card is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    _require_board_access(card.board_id, user, db)

    update_fields = {}
    if body.title is not None:
        update_fields["title"] = body.title
    if body.description is not None:
        update_fields["description"] = body.description
    if body.due_date is not None:
        update_fields["due_date"] = body.due_date
    if body.assignee is not None:
        update_fields["assignee"] = body.assignee

    updated = db.update_card(card_id, update_fields)
    return _card_to_out(updated)


@router.delete("/api/cards/{card_id}", response_model=SuccessResponse)
def delete_card(
    card_id: int,
    user: User = Depends(get_current_user),
    db: MockDatabaseService = Depends(get_db),
):
    card = db.get_card(card_id)
    if card is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    _require_board_access(card.board_id, user, db)
    db.delete_card(card_id)
    return SuccessResponse(success=True)


@router.patch("/api/cards/{card_id}/move", response_model=CardOut)
def move_card(
    card_id: int,
    body: MoveCardRequest,
    user: User = Depends(get_current_user),
    db: MockDatabaseService = Depends(get_db),
):
    card = db.get_card(card_id)
    if card is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    _require_board_access(card.board_id, user, db)
    moved = db.move_card(card_id, body.new_column, body.new_position)
    return _card_to_out(moved)


@router.patch("/api/boards/{board_id}/reorder", response_model=SuccessResponse)
def reorder_cards(
    board_id: int,
    body: ReorderRequest,
    user: User = Depends(get_current_user),
    db: MockDatabaseService = Depends(get_db),
):
    _require_board_access(board_id, user, db)
    success = db.reorder_cards(board_id, body.column, body.card_ids)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Card list mismatch")
    return SuccessResponse(success=True)
