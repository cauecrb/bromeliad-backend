from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.user_repository import user_repository
from app.schemas.user import UserCreate
from app.services import audit_service


def register_user(db: Session, data: UserCreate):
    if user_repository.get_by_email(db, data.email):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "E-mail já cadastrado")

    user = user_repository.create(
        db,
        {
            "name": data.name,
            "email": data.email,
            "hashed_password": hash_password(data.password),
            "role": data.role,
        },
    )
    audit_service.log_action(
        db, user_id=user.id, action="create", entity="user", entity_id=str(user.id)
    )
    return user


def authenticate(db: Session, email: str, password: str) -> str:
    user = user_repository.get_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Credenciais inválidas")
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Usuário desativado")

    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    audit_service.log_action(
        db, user_id=user.id, action="login", entity="user", entity_id=str(user.id)
    )
    return token
