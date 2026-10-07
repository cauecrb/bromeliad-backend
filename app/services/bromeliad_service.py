from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.bromeliad_repository import bromeliad_repository
from app.schemas.bromeliad import BromeliadCreate, BromeliadUpdate
from app.services import audit_service


def create_bromeliad(db: Session, data: BromeliadCreate, current_user: User):
    if bromeliad_repository.get_by_accession_code(db, data.accession_code):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Código de acesso já cadastrado"
        )

    bromeliad = bromeliad_repository.create(db, data.model_dump())
    audit_service.log_action(
        db,
        user_id=current_user.id,
        action="create",
        entity="bromeliad",
        entity_id=str(bromeliad.id),
        details={"accession_code": bromeliad.accession_code},
    )
    return bromeliad


def get_bromeliad(db: Session, bromeliad_id: UUID):
    bromeliad = bromeliad_repository.get(db, bromeliad_id)
    if not bromeliad:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Bromélia não encontrada")
    return bromeliad


def list_bromeliads(db: Session, skip: int = 0, limit: int = 100):
    return bromeliad_repository.list(db, skip=skip, limit=limit)


def update_bromeliad(db: Session, bromeliad_id: UUID, data: BromeliadUpdate, current_user: User):
    bromeliad = get_bromeliad(db, bromeliad_id)
    changes = data.model_dump(exclude_unset=True)
    bromeliad = bromeliad_repository.update(db, bromeliad, changes)

    audit_service.log_action(
        db,
        user_id=current_user.id,
        action="update",
        entity="bromeliad",
        entity_id=str(bromeliad.id),
        details={"changed_fields": list(changes.keys())},
    )
    return bromeliad


def delete_bromeliad(db: Session, bromeliad_id: UUID, current_user: User):
    bromeliad = get_bromeliad(db, bromeliad_id)
    bromeliad_repository.delete(db, bromeliad)

    audit_service.log_action(
        db,
        user_id=current_user.id,
        action="delete",
        entity="bromeliad",
        entity_id=str(bromeliad_id),
    )
