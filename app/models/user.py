"""
Model de usuário.

O campo `role` é um enum simples (não uma tabela de permissões separada)
de propósito — o projeto pediu pra não complicar demais. Se no futuro
precisar de permissões mais finas (ex: "pode editar mas não excluir"),
dá pra evoluir pra uma tabela `permissions` sem quebrar o resto: só o
model e o `deps.py` (quem checa a permissão) mudam.
"""
import enum

from sqlalchemy import String, Boolean, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import TimestampedModel


class UserRole(str, enum.Enum):
    ADMIN = "admin"      # acesso total, inclusive gestão de usuários
    EDITOR = "editor"    # pode cadastrar/editar bromélias
    VIEWER = "viewer"    # só consulta


class User(TimestampedModel):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"), default=UserRole.VIEWER
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
