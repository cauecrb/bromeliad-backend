from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.core.database import get_db
from app.models.audit_log import AuditLog
from app.models.user import UserRole

router = APIRouter(prefix="/audit-logs", tags=["audit"])


@router.get("")
def list_logs(
    db: Session = Depends(get_db),
    _=Depends(require_role(UserRole.ADMIN)),
    skip: int = 0,
    limit: int = 100,
):
    stmt = select(AuditLog).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit)
    return db.scalars(stmt).all()
