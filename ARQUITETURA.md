# Sistema de Cadastro e Consulta de Bromélias — Documento de Arquitetura

> Guia de referência das decisões técnicas do projeto. Serve como fonte
> única de verdade para consultar "por que escolhemos X" e "onde mexer
> quando precisar mudar Y".

---

## 1. Visão geral

Sistema web para cadastro e consulta de bromélias, com controle de acesso
por usuário/permissão e trilha de auditoria (quem fez o quê). Projeto
pensado para uso real por uma pessoa externa e também como peça de
portfólio.

**Premissas que guiaram todas as decisões abaixo:**
- Sem custo de infraestrutura (tudo em free tier)
- Precisa ficar no ar de forma persistente (não pode "expirar" sozinho)
- Modularização alta: trocar peça (banco, storage, host) não pode quebrar
  o resto do sistema
- Schema do banco ainda não é definitivo — o design tem que tolerar
  campos sendo adicionados/removidos sem gerar refatoração em cascata
- Sem overengineering — só as ferramentas que resolvem um problema real

---

## 2. Stack escolhida

| Camada | Escolha | Motivo |
|---|---|---|
| Backend | **Python + FastAPI** | Autor já domina Python (automação, API OpenAI); FastAPI entra no Render sem precisar de Docker (embora Docker tenha sido adotado por opção, ver seção 5); mais alinhado ao restante do portfólio |
| Banco de dados | **Supabase (PostgreSQL)** | Persistente — não expira como o Postgres grátis do próprio Render (que dura só 30 dias). Free tier pausa após 7 dias *sem nenhum acesso*, mas os dados não são apagados; uso real semanal evita a pausa |
| Storage (fotos/documentos) | **Supabase Storage** (ou Cloudflare R2 como alternativa) | Mantém tudo no mesmo painel do banco; R2 fica de reserva caso o limite de 1GB do Supabase Storage aperte (10GB grátis, sem custo de egress) |
| Frontend | **React**, hospedado no **Vercel** | Hospedagem estática gratuita permanente, deploy automático via Git |
| Deploy do backend | **Render**, via **Docker** | Render tem free tier com suporte total a Docker (build a partir de Dockerfile ou imagem pronta); optamos por Docker (em vez do runtime nativo) por portabilidade — a mesma imagem sobe em Railway/Fly.io/Cloud Run se o Render deixar de servir no futuro — e por manter ambiente idêntico entre dev, teste e produção |

### Alternativas descartadas e por quê
- **PythonAnywhere**: free tier enfraquecido (web app expira em 1 mês, precisa renovar manualmente, sem suporte)
- **PHP**: cogitado por experiência prévia do autor, mas como o projeto tende a ser "puramente web sem cálculo pesado", isso não pesava a favor de nenhum dos dois; optou-se por Python para focar a stack de portfólio. PHP funcionaria igualmente bem com Supabase (conexão via PDO nativo), a diferença estaria só no deploy (PHP exige Docker no Render; Python tem runtime nativo)
- **Postgres do próprio Render como banco**: descartado por expirar em 30 dias — inviável para um sistema de uso contínuo por terceiro

---

## 3. Arquitetura em camadas

Estrutura pensada para que trocar uma peça (banco, storage, provedor)
nunca exija tocar em código de regra de negócio.

```
app/
├── core/           # Config central, conexão com banco, segurança (hash/JWT)
├── models/         # Tabelas (SQLAlchemy) — só a estrutura de dados
├── schemas/        # Formato de entrada/saída da API (Pydantic)
├── repositories/   # Acesso a dados — CRUD genérico reaproveitável
├── storage/        # Interface abstrata para upload de arquivos
├── services/       # Regra de negócio — única camada que fala com repositories/storage
└── api/
    ├── deps.py     # Autenticação e checagem de permissão
    └── routes/     # Endpoints HTTP — só falam com services
```

**Regra de dependência:** rota → service → repository/storage → model.
Nunca o inverso, e nunca uma rota pulando direto pro banco.

### Peças-chave da modularização
- **`BaseRepository` genérico**: qualquer tabela nova reaproveita create/get/update/delete sem reescrever nada
- **`StorageProvider` (interface abstrata)**: hoje implementado pra Supabase Storage; trocar para Cloudflare R2 no futuro = só uma nova classe, zero mudança no resto do app
- **`schemas` com campos opcionais + `exclude_unset=True`**: adicionar/remover campo em uma tabela não quebra os updates parciais existentes
- **`config.py` centralizado**: toda credencial/URL de serviço externo vive em variável de ambiente — nunca hardcoded em código de negócio

---

## 4. Módulos implementados

### 4.1 Autenticação e permissão (`users`)
- Cadastro (`POST /auth/register`) e login (`POST /auth/login`, retorna JWT)
- Senhas com hash bcrypt, nunca armazenadas em texto puro
- Papéis (`role`): `admin`, `editor`, `viewer` — controle simples por enum,
  sem tabela de permissões separada (decisão consciente para não
  complicar; pode evoluir para permissões finas no futuro sem quebrar o
  restante do sistema)
- `require_role(...)` em `api/deps.py`: dependência do FastAPI que bloqueia
  rota para quem não tem o papel exigido

### 4.2 Log de auditoria (`audit_logs`)
- Tabela única e genérica (`user_id`, `action`, `entity`, `entity_id`,
  `details` em JSON) — não é uma tabela de log por entidade, então
  mudanças de schema em outras tabelas não exigem migração aqui
- **Decisão importante**: o registro do log é **explícito**, feito à mão
  dentro de cada `service` (ex: `auth_service` chama
  `audit_service.log_action(...)` depois de criar usuário ou logar).
  Optamos por não automatizar via hooks/eventos para manter o código
  fácil de seguir e depurar
- Consulta somente para `admin` (`GET /audit-logs`)

---

## 5. Containerização (Docker)

Decisão: **backend containerizado desde o início.**

- Render, Railway e Google Cloud Run aceitam Docker no free tier sem
  restrição adicional em relação ao runtime nativo
- Ganhos: portabilidade entre provedores, ambiente idêntico em
  dev/teste/produção, e reforça a modularização (o backend vira uma
  unidade isolada do host)
- Custo: uma camada extra de configuração (`Dockerfile`), aceitável para
  o tamanho do projeto

---

## 6. Estratégia de testes automatizados

Definida, ainda não implementada. Camadas planejadas, sem excesso de
ferramentas:

| Tipo | Ferramenta | O que cobre |
|---|---|---|
| Unitário | `pytest` | `services/` isolados, com repository "mockado" |
| Integração | `pytest` + Postgres via Docker (local e no CI) | Repository + banco real, mesmo dialect usado em produção (suporta UUID/JSONB) |
| Ponta a ponta (API) | `TestClient` do FastAPI (usa `httpx`) | Rotas HTTP reais (`/auth/login`, `/audit-logs`, etc.) |
| Dados de teste | `Faker` / `factory_boy` | Gerar usuários/bromélias fictícios sem massa de dados manual |
| CI | GitHub Actions (grátis) | Roda `pytest` a cada push, sobe Postgres como serviço do próprio workflow |

Testes nunca rodam contra o Supabase de produção — sempre contra um
Postgres isolado (Docker local ou serviço do CI).

---

## 7. Em aberto / próximos passos

- [ ] Modelagem das tabelas do domínio de bromélias (campos, relação com
      fotos/documentos) — schema ainda não é definitivo, será validado
      com o autor antes de fechar
- [ ] Implementar `StorageProvider` para Supabase Storage
- [ ] CRUD de bromélias (models → schemas → repository → service → rotas)
- [ ] Escrever `Dockerfile` e `docker-compose.yml` (backend + Postgres local)
- [ ] Montar suíte de testes (pytest + fixtures + Postgres via Docker)
- [ ] Configurar GitHub Actions (lint + testes a cada push)
- [ ] Deploy no Render a partir da imagem Docker
