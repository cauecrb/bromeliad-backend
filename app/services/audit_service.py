"""
Service de auditoria.

Regra do projeto: NENHUM outro código escreve na tabela audit_logs
diretamente — sempre passa por `log_action`. Isso mantém um único
lugar responsável pelo formato do log, então se amanhã decidirmos
mudar como/onde o log é guardado (ex: mandar pra um serviço externo
tipo Sentry/Datadog além do banco), só este arquivo muda.
"""
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def log_action(
    db: Session,
    *,
    user_id: UUID | None,
    action: str,
    entity: str,
    entity_id: str | None = None,
    details: dict | None = None,
) -> AuditLog:
    entry = AuditLog(
        user_id=user_id,
        action=action,
        entity=entity,
        entity_id=entity_id,
        details=details,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
