"""
Ponto único de importação de todos os models.

O Alembic (via `target_metadata` em alembic/env.py) só consegue gerar
migrations automáticas pra tabelas que estiverem registradas em
`Base.metadata` — e isso só acontece se o módulo do model for
importado em algum lugar antes do autogenerate rodar. Centralizar
aqui evita o erro clássico de "esqueci de importar o model novo e o
Alembic não gerou a tabela dele".
"""
from app.models.base import Base  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.audit_log import AuditLog  # noqa: F401
from app.models.bromeliad import Bromeliad  # noqa: F401
from app.models.bromeliad_media import BromeliadMedia  # noqa: F401
