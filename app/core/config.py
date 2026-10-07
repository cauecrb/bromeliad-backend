"""
Configurações centrais da aplicação.

Tudo que muda dependendo do ambiente (banco, storage, chaves) vive aqui,
lido a partir de variáveis de ambiente (.env). Assim, trocar de provedor
(ex: Supabase -> outro Postgres, ou Supabase Storage -> Cloudflare R2)
nunca exige mexer em código de negócio — só nessas variáveis.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Banco de dados ---
    # String de conexão padrão SQLAlchemy. Hoje aponta pro Supabase (Postgres),
    # mas como é só uma URL, trocar de provedor Postgres é só mudar aqui.
    database_url: str = "postgresql+psycopg2://user:password@localhost:5432/bromeliads"

    # --- Storage (fotos/documentos) ---
    # "supabase" ou "r2" — usado pela factory em storage/__init__.py
    # pra decidir qual implementação de StorageProvider instanciar.
    storage_provider: str = "supabase"

    supabase_url: str | None = None
    supabase_key: str | None = None
    supabase_bucket: str = "bromeliads"

    r2_endpoint: str | None = None
    r2_access_key: str | None = None
    r2_secret_key: str | None = None
    r2_bucket: str | None = None

    # --- App ---
    api_prefix: str = "/api/v1"
    debug: bool = True

    # Origens do frontend autorizadas a chamar a API (CORS).
    # Separadas por vírgula no .env — ex: "http://localhost:5173,https://meuapp.vercel.app"
    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    """Cache simples — evita reler o .env a cada request."""
    return Settings()
