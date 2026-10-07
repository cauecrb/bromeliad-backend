# Sistema de Cadastro e Consulta de Bromélias

Sistema web para cadastro, consulta e gestão de bromélias, com controle
de acesso por usuário/permissão e trilha de auditoria.

> Documentação completa das decisões técnicas e arquitetura em
> [`ARQUITETURA.md`](./ARQUITETURA.md).

## Stack

- **Backend:** Python + FastAPI
- **Banco de dados:** PostgreSQL (Supabase)
- **Storage:** Supabase Storage (fotos e documentos)
- **Frontend:** React (repositório separado)
- **Containerização:** Docker
- **Deploy:** Render

## Status do projeto

🚧 Em desenvolvimento — módulos de autenticação e log de auditoria
implementados. Modelagem do domínio de bromélias ainda em andamento.

## Estrutura

```
app/
├── core/           # Configuração, conexão com banco, segurança (hash/JWT)
├── models/         # Tabelas (SQLAlchemy)
├── schemas/        # Formato de entrada/saída da API (Pydantic)
├── repositories/   # Acesso a dados (CRUD genérico)
├── storage/        # Interface de upload de arquivos
├── services/       # Regras de negócio
└── api/
    ├── deps.py     # Autenticação e permissão
    └── routes/     # Endpoints HTTP
```

## Como rodar localmente

### Opção 1 — sem Docker

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # edite com suas credenciais do Supabase
uvicorn app.main:app --reload
```

### Opção 2 — com Docker

```bash
cp .env.example .env
docker compose up --build
```

Em ambos os casos, a API sobe em `http://localhost:8000` e a
documentação interativa (Swagger) fica em `http://localhost:8000/docs`.

## Variáveis de ambiente

Veja [`.env.example`](./.env.example) para a lista completa.

## Endpoints implementados

| Método | Rota | Descrição | Acesso |
|---|---|---|---|
| POST | `/api/v1/auth/register` | Cadastro de usuário | Público |
| POST | `/api/v1/auth/login` | Login (retorna JWT) | Público |
| GET | `/api/v1/audit-logs` | Consulta ao log de auditoria | Admin |

## Roadmap

Ver seção "Em aberto" em [`ARQUITETURA.md`](./ARQUITETURA.md).
