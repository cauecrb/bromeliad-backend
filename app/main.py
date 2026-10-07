from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, audit_logs, bromeliads, bromeliad_media
from app.core.config import get_settings

settings = get_settings()
app = FastAPI(title="Sistema de Bromélias")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(audit_logs.router, prefix=settings.api_prefix)
app.include_router(bromeliads.router, prefix=settings.api_prefix)
app.include_router(bromeliad_media.router, prefix=settings.api_prefix)


@app.get("/health")
def health():
    return {"status": "ok"}
