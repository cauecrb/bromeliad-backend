"""
Log de auditoria — "quem fez o quê".

De propósito NÃO é uma tabela por entidade (ex: "bromeliad_log",
"usuario_log"). É uma única tabela genérica: guarda quem (`user_id`),
o quê (`action`), em qual entidade (`entity` + `entity_id`) e detalhes
extras num JSON solto (`details`). Isso significa que quando o model
de bromélia ganhar ou perder campos, o log NÃO precisa de migração —
ele não tem coluna fixa por campo, só o JSON.
"""
from uuid import UUID

from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import TimestampedModel


class AuditLog(TimestampedModel):
    __tablename__ = "audit_logs"

    user_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    action: Mapped[str] = mapped_column(String(50))       # "create", "update", "delete", "login"
    entity: Mapped[str] = mapped_column(String(50))        # "bromeliad", "user", etc.
    entity_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    details: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
