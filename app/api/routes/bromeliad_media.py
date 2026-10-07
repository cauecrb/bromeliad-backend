from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.core.database import get_db
from app.models.user import User, UserRole
from app.schemas.bromeliad_media import BromeliadMediaCreate, BromeliadMediaOut
from app.services import bromeliad_media_service

router = APIRouter(prefix="/bromeliads/{bromeliad_id}/media", tags=["bromeliad-media"])

can_write = require_role(UserRole.ADMIN, UserRole.EDITOR)


@router.post("", response_model=BromeliadMediaOut)
def add(
    bromeliad_id: UUID,
    data: BromeliadMediaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(can_write),
):
    return bromeliad_media_service.add_media(db, bromeliad_id, data, current_user)


@router.get("", response_model=list[BromeliadMediaOut])
def list_all(
    bromeliad_id: UUID,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return bromeliad_media_service.list_media(db, bromeliad_id)


@router.delete("/{media_id}", status_code=204)
def delete(
    bromeliad_id: UUID,
    media_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(can_write),
):
    bromeliad_media_service.delete_media(db, media_id, current_user)
