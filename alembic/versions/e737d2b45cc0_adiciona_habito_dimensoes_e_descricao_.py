"""adiciona habito, dimensoes e descricao em bromeliads

Revision ID: e737d2b45cc0
Revises: 36a215a52bf2
Create Date: 2026-10-07 11:29:53.593865

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'e737d2b45cc0'
down_revision = '36a215a52bf2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # O autogenerate esquece de criar o tipo ENUM antes de usá-lo numa
    # coluna adicionada a uma tabela já existente (só faz isso sozinho
    # quando a tabela é criada do zero). Criamos explicitamente aqui.
    growth_habit_enum = postgresql.ENUM(
        "EPIFITA", "TERRESTRE", "RUPICOLA", name="growth_habit"
    )
    growth_habit_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "bromeliads", sa.Column("growth_habit", growth_habit_enum, nullable=True)
    )
    op.add_column(
        "bromeliads", sa.Column("height_cm", sa.Numeric(precision=6, scale=1), nullable=True)
    )
    op.add_column(
        "bromeliads", sa.Column("width_cm", sa.Numeric(precision=6, scale=1), nullable=True)
    )
    op.add_column("bromeliads", sa.Column("description", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("bromeliads", "description")
    op.drop_column("bromeliads", "width_cm")
    op.drop_column("bromeliads", "height_cm")
    op.drop_column("bromeliads", "growth_habit")

    # Remove o tipo ENUM também — sem isso, rodar upgrade de novo depois
    # de um downgrade falharia com "type already exists".
    postgresql.ENUM(name="growth_habit").drop(op.get_bind(), checkfirst=True)
