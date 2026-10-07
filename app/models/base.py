"""
Base compartilhada por todos os models.

Qualquer tabela nova (ex: "cuidados", "fornecedores") deve herdar de
`Base` e ganha automaticamente id, created_at e updated_at — evita
repetir esses 3 campos em cada model novo.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TimestampedModel(Base):
    """Mixin abstrato: id (UUID) + created_at + updated_at automáticos."""

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
