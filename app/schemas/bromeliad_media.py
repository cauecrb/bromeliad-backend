import uuid
from datetime import datetime

from pydantic import BaseModel, model_validator

from app.models.bromeliad_media import MediaType


class BromeliadMediaCreate(BaseModel):
    # Preencha storage_key (upload já feito no R2) OU external_url
    # (link pra algo já hospedado na internet) — nunca os dois, nunca
    # nenhum. Validado em model_validator abaixo, não no banco.
    storage_key: str | None = None
    external_url: str | None = None

    media_type: MediaType
    caption: str | None = None
    is_primary: bool = False

    @model_validator(mode="after")
    def exactly_one_source(self):
        if bool(self.storage_key) == bool(self.external_url):
            raise ValueError(
                "Informe exatamente uma origem: storage_key (upload) ou external_url (link)"
            )
        return self


class BromeliadMediaOut(BaseModel):
    id: uuid.UUID
    bromeliad_id: uuid.UUID
    storage_key: str | None
    external_url: str | None
    source_type: str
    media_type: MediaType
    caption: str | None
    is_primary: bool
    created_at: datetime

    model_config = {"from_attributes": True}
