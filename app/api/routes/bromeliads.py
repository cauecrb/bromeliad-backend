from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.core.database import get_db
from app.models.user import User, UserRole
from app.schemas.bromeliad import BromeliadCreate, BromeliadOut, BromeliadUpdate
from app.services import bromeliad_service

router = APIRouter(prefix="/bromeliads", tags=["bromeliads"])

# Quem pode cadastrar/editar/excluir — leitura fica liberada a qualquer
# usuário autenticado (inclusive viewer), só a escrita é restrita.
can_write = require_role(UserRole.ADMIN, UserRole.EDITOR)


@router.post("", response_model=BromeliadOut)
def create(
    data: BromeliadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(can_write),
):
    return bromeliad_service.create_bromeliad(db, data, current_user)


@router.get("", response_model=list[BromeliadOut])
def list_all(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
):
    return bromeliad_service.list_bromeliads(db, skip, limit)


@router.get("/{bromeliad_id}", response_model=BromeliadOut)
def get_one(
    bromeliad_id: UUID,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return bromeliad_service.get_bromeliad(db, bromeliad_id)


@router.patch("/{bromeliad_id}", response_model=BromeliadOut)
def update(
    bromeliad_id: UUID,
    data: BromeliadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(can_write),
):
    return bromeliad_service.update_bromeliad(db, bromeliad_id, data, current_user)


@router.delete("/{bromeliad_id}", status_code=204)
def delete(
    bromeliad_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(can_write),
):
    bromeliad_service.delete_bromeliad(db, bromeliad_id, current_user)
