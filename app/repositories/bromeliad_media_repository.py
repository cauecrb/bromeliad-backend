from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.bromeliad_media import BromeliadMedia
from app.repositories.base import BaseRepository


class BromeliadMediaRepository(BaseRepository[BromeliadMedia]):
    def list_by_bromeliad(self, db: Session, bromeliad_id: UUID) -> list[BromeliadMedia]:
        stmt = (
            select(BromeliadMedia)
            .where(BromeliadMedia.bromeliad_id == bromeliad_id)
            .order_by(BromeliadMedia.created_at)
        )
        return list(db.scalars(stmt).all())

    def clear_primary(self, db: Session, bromeliad_id: UUID) -> None:
        """Tira a marca de capa de qualquer outra mídia da mesma bromélia
        — usado antes de marcar uma nova como principal."""
        stmt = select(BromeliadMedia).where(
            BromeliadMedia.bromeliad_id == bromeliad_id, BromeliadMedia.is_primary.is_(True)
        )
        for media in db.scalars(stmt).all():
            media.is_primary = False
        db.commit()


bromeliad_media_repository = BromeliadMediaRepository(BromeliadMedia)
