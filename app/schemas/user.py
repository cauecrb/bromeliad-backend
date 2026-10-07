"""
Schemas de usuário.

Três formatos separados de propósito:
- UserCreate: o que a rota de cadastro aceita (inclui senha em texto puro)
- UserOut: o que a API devolve (NUNCA inclui a senha)
- UserUpdate: todos os campos opcionais, com exclude_unset=True no service
  — assim, adicionar um campo novo no futuro não quebra updates parciais.
"""
import uuid

from pydantic import BaseModel, EmailStr

from app.models.user import UserRole


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.VIEWER


class UserUpdate(BaseModel):
    name: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None


class UserOut(BaseModel):
    id: uuid.UUID
    name: str
    email: EmailStr
    role: UserRole
    is_active: bool

    model_config = {"from_attributes": True}
