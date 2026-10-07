from uuid import UUID

from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.bromeliad_media_repository import bromeliad_media_repository
from app.schemas.bromeliad_media import BromeliadMediaCreate
from app.services import audit_service
from app.services.bromeliad_service import get_bromeliad  # garante que a bromélia existe


def add_media(db: Session, bromeliad_id: UUID, data: BromeliadMediaCreate, current_user: User):
    get_bromeliad(db, bromeliad_id)  # 404 se não existir

    if data.is_primary:
        bromeliad_media_repository.clear_primary(db, bromeliad_id)

    media = bromeliad_media_repository.create(
        db, {**data.model_dump(), "bromeliad_id": bromeliad_id}
    )

    audit_service.log_action(
        db,
        user_id=current_user.id,
        action="create",
        entity="bromeliad_media",
        entity_id=str(media.id),
        details={"bromeliad_id": str(bromeliad_id), "media_type": data.media_type.value},
    )
    return media


def list_media(db: Session, bromeliad_id: UUID):
    get_bromeliad(db, bromeliad_id)
    return bromeliad_media_repository.list_by_bromeliad(db, bromeliad_id)


def delete_media(db: Session, media_id: UUID, current_user: User):
    media = bromeliad_media_repository.get(db, media_id)
    if media:
        bromeliad_media_repository.delete(db, media)
        audit_service.log_action(
            db,
            user_id=current_user.id,
            action="delete",
            entity="bromeliad_media",
            entity_id=str(media_id),
        )
