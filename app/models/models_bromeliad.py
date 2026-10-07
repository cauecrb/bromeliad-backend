"""
Model principal do domínio: Bromeliad.

Estrutura em 4 blocos, seguindo o padrão usado por jardins botânicos
(registro de "accession"), o vocabulário Darwin Core pra identidade
taxonômica, e o Registro Internacional de Cultivares de Bromélia (BSI)
pros campos de característica física:

1. Identidade taxonômica — nome científico, família, nome popular,
   parentagem (se for híbrido)
2. Registro de acesso — código único, origem, data, status da planta
3. Características físicas — hábito de crescimento, dimensões e
   descrição (texto livre; ganha busca de texto completo quando
   implementarmos a tela de consulta)
4. `extra_info` (JSONB) — campo flexível pra tudo que ainda não tem
   coluna própria; migra pra coluna fixa via Alembic quando o formato
   definitivo do laboratório ficar claro, sem quebrar o que já existe
"""
import enum
from datetime import date
from decimal import Decimal

from sqlalchemy import String, Date, Enum, Numeric, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import TimestampedModel


class BromeliadStatus(str, enum.Enum):
    ATIVA = "ativa"                # viva, na coleção
    EM_PROPAGACAO = "em_propagacao"
    DOADA = "doada"
    MORTA = "morta"


class GrowthHabit(str, enum.Enum):
    EPIFITA = "epifita"
    TERRESTRE = "terrestre"
    RUPICOLA = "rupicola"


class Bromeliad(TimestampedModel):
    __tablename__ = "bromeliads"

    # --- Identidade taxonômica ---
    genus: Mapped[str] = mapped_column(String(80))
    specific_epithet: Mapped[str | None] = mapped_column(String(80), nullable=True)
    infraspecific_epithet: Mapped[str | None] = mapped_column(String(80), nullable=True)
    scientific_name_authorship: Mapped[str | None] = mapped_column(String(120), nullable=True)
    family: Mapped[str] = mapped_column(String(80), default="Bromeliaceae")
    common_name: Mapped[str | None] = mapped_column(String(120), nullable=True)

    # Preenchido só se for híbrido — planta-mãe x planta-pai.
    # Texto livre por enquanto (não uma FK pra outro Bromeliad): a
    # genealogia completa de cruzamento é um refinamento futuro.
    hybrid_parentage: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # --- Registro de acesso (accession) ---
    accession_code: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    acquisition_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)  # proveniência
    status: Mapped[BromeliadStatus] = mapped_column(
        Enum(BromeliadStatus, name="bromeliad_status"), default=BromeliadStatus.ATIVA
    )

    # Quem cadastrou fica registrado no audit_log (action="create",
    # entity="bromeliad") — não duplicamos essa informação aqui.

    # --- Características físicas ---
    growth_habit: Mapped[GrowthHabit | None] = mapped_column(
        Enum(GrowthHabit, name="growth_habit"), nullable=True
    )
    height_cm: Mapped[Decimal | None] = mapped_column(Numeric(6, 1), nullable=True)
    width_cm: Mapped[Decimal | None] = mapped_column(Numeric(6, 1), nullable=True)

    # Descrição morfológica/distintiva em texto livre — o que o
    # Registro da BSI pede por escrito (cor, forma, textura, etc.).
    # Candidata natural a busca de texto completo (tsvector) quando
    # montarmos a tela de consulta.
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # --- Campo flexível ---
    extra_info: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    @property
    def scientific_name(self) -> str:
        """Nome científico completo montado a partir das partes —
        é o que vai no campo em destaque da tela de consulta."""
        parts = [self.genus]
        if self.specific_epithet:
            parts.append(self.specific_epithet)
        if self.infraspecific_epithet:
            parts.append(self.infraspecific_epithet)
        name = " ".join(parts)
        if self.scientific_name_authorship:
            name = f"{name} {self.scientific_name_authorship}"
        return name
