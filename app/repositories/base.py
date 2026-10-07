"""
Repository genérico.

Objetivo: nenhuma tabela nova deveria precisar reescrever create/get/update/
delete do zero. Qualquer model que herde de `Base` pode usar
`BaseRepository(Model)` diretamente, ou uma subclasse só pra métodos
extras (ex: `get_by_email`, ver user_repository.py).

Isso é o que segura o projeto modular na prática: se amanhã aparecer uma
tabela "cuidados" ou "fornecedores", 90% do CRUD já existe aqui.
"""
from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType]):
        self.model = model

    def get(self, db: Session, id: UUID) -> ModelType | None:
        return db.get(self.model, id)

    def list(self, db: Session, skip: int = 0, limit: int = 100) -> list[ModelType]:
        stmt = select(self.model).offset(skip).limit(limit)
        return list(db.scalars(stmt).all())

    def create(self, db: Session, data: dict) -> ModelType:
        obj = self.model(**data)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def update(self, db: Session, obj: ModelType, data: dict) -> ModelType:
        # data já deve vir só com os campos que realmente mudaram
        # (schemas usam exclude_unset=True) — não sobrescreve o resto.
        for field, value in data.items():
            setattr(obj, field, value)
        db.commit()
        db.refresh(obj)
        return obj

    def delete(self, db: Session, obj: ModelType) -> None:
        db.delete(obj)
        db.commit()
