"""
Engine e sessão do SQLAlchemy.

Nenhum outro módulo deve importar `create_engine` diretamente — tudo passa
por aqui. Se um dia trocar de Postgres gerenciado (Supabase -> outro),
só a `database_url` no .env muda; este arquivo não precisa ser tocado.
"""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import get_settings

settings = get_settings()

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency do FastAPI — abre e fecha a sessão a cada request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
