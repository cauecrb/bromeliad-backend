"""
Dependências de autenticação/autorização.

`get_current_user`: qualquer rota protegida usa isso pra saber quem
está chamando.
`require_role`: fábrica de dependência — `require_role(UserRole.ADMIN)`
bloqueia a rota pra quem não tem aquele papel. Novas regras de
permissão nascem aqui, sem tocar nas rotas em si.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User, UserRole
from app.repositories.user_repository import user_repository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    credentials_error = HTTPException(
        status.HTTP_401_UNAUTHORIZED, "Não foi possível validar as credenciais"
    )
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise credentials_error

    user = user_repository.get(db, payload["sub"])
    if not user or not user.is_active:
        raise credentials_error
    return user


def require_role(*allowed: UserRole):
    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN, "Sem permissão para essa ação"
            )
        return user

    return checker
