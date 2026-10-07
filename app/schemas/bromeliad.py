import uuid
from datetime import date, datetime

from pydantic import BaseModel

from app.models.bromeliad import BromeliadStatus


class BromeliadCreate(BaseModel):
    genus: str
    specific_epithet: str | None = None
    infraspecific_epithet: str | None = None
    scientific_name_authorship: str | None = None
    family: str = "Bromeliaceae"
    common_name: str | None = None
    hybrid_parentage: str | None = None

    accession_code: str
    acquisition_date: date | None = None
    source: str | None = None
    status: BromeliadStatus = BromeliadStatus.ATIVA

    extra_info: dict | None = None


class BromeliadUpdate(BaseModel):
    """Todos os campos opcionais — o service aplica só o que veio
    preenchido (exclude_unset=True), então adicionar/remover campo aqui
    no futuro não quebra updates parciais já existentes."""

    genus: str | None = None
    specific_epithet: str | None = None
    infraspecific_epithet: str | None = None
    scientific_name_authorship: str | None = None
    family: str | None = None
    common_name: str | None = None
    hybrid_parentage: str | None = None

    acquisition_date: date | None = None
    source: str | None = None
    status: BromeliadStatus | None = None

    extra_info: dict | None = None


class BromeliadOut(BaseModel):
    id: uuid.UUID
    scientific_name: str  # property calculada no model — vai no destaque da tela
    genus: str
    specific_epithet: str | None
    infraspecific_epithet: str | None
    scientific_name_authorship: str | None
    family: str
    common_name: str | None
    hybrid_parentage: str | None

    accession_code: str
    acquisition_date: date | None
    source: str | None
    status: BromeliadStatus

    extra_info: dict | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
