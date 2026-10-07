"""
Model de mídia — uma linha por arquivo (foto, desenho ou documento)
vinculado a uma bromélia. Separado da tabela principal de propósito:
uma bromélia pode ter N mídias, e adicionar/remover uma foto nunca
deveria significar alterar a tabela `bromeliads`.

Duas formas de origem pra cada mídia (o laboratório escolhe uma):
- upload de verdade (`storage_key`, arquivo próprio salvo no R2) — o
  caminho principal, pensado pra foto/documento tirado pelo laboratório
- `external_url` (link secundário) — caso queiram só referenciar uma
  imagem/documento que já existe em outro site, sem fazer upload
Exatamente um dos dois deve estar preenchido — validado no service,
não aqui no model, pra manter a definição de dado simples.
"""
import enum
import uuid

from sqlalchemy import String, Boolean, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import TimestampedModel


class MediaType(str, enum.Enum):
    FOTO = "foto"
    DESENHO = "desenho"
    DOCUMENTO = "documento"


class BromeliadMedia(TimestampedModel):
    __tablename__ = "bromeliad_media"

    bromeliad_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("bromeliads.id"), index=True
    )

    # Caminho do objeto no bucket R2 — NÃO a URL pública completa.
    # Trocar de domínio/CDN no futuro não vira migração de dado.
    # Nulo quando a mídia é um link externo (ver external_url).
    storage_key: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Link externo — alternativa ao upload, pra quando o laboratório só
    # quer referenciar uma imagem/documento que já existe na internet.
    external_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    media_type: Mapped[MediaType] = mapped_column(Enum(MediaType, name="media_type"))
    caption: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Marca a foto de capa exibida no card do catálogo.
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)

    @property
    def source_type(self) -> str:
        return "upload" if self.storage_key else "link"
