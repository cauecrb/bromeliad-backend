from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.bromeliad import Bromeliad
from app.repositories.base import BaseRepository


class BromeliadRepository(BaseRepository[Bromeliad]):
    def get_by_accession_code(self, db: Session, code: str) -> Bromeliad | None:
        stmt = select(Bromeliad).where(Bromeliad.accession_code == code)
        return db.scalars(stmt).first()


bromeliad_repository = BromeliadRepository(Bromeliad)
