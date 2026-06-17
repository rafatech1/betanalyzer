# BetAnalyzer

Sistema de análise de apostas de futebol orientado a **valor esperado (EV+)**, não a taxa de acerto. Compara a probabilidade estimada por modelo com a probabilidade implícita das odds (já sem o overround da casa) para identificar oportunidades com EV positivo.

> **Aviso de risco:** este sistema não garante resultados. Apostas envolvem risco de perda de capital. Use sempre as ferramentas de controle de banca (Kelly fracionado, máx. 25% do Kelly) e nunca aposte mais do que pode perder.

## Stack

- **Backend:** Python 3.12 + FastAPI + SQLAlchemy 2.0 (async) + Alembic + PostgreSQL 16 + Redis
- **Frontend:** Next.js 14 (App Router) + Tailwind CSS + TypeScript
- **IA:** API da Anthropic (Claude) para análise qualitativa e síntese
- **Dados:** API-Football + The Odds API
- **Deploy:** Docker Compose + Nginx + Let's Encrypt em VPS Ubuntu (ARM64 compatível)

## Estrutura do monorepo

```
betanalyzer/
├── backend/          # FastAPI, modelos SQLAlchemy, Alembic
│   ├── app/
│   │   ├── core/     # config, logging
│   │   ├── db/       # engine, sessão, redis
│   │   ├── models/   # leagues, teams, fixtures, odds, analyses, bets, bankroll
│   │   ├── routers/
│   │   ├── schemas/
│   │   └── services/
│   ├── alembic/
│   └── tests/
├── frontend/         # Next.js + Tailwind
│   └── src/
│       ├── app/
│       ├── components/
│       ├── lib/
│       └── types/
├── scripts/
│   └── pg_backup.sh   # backup diário do Postgres (cron)
├── docker-compose.yml        # desenvolvimento
├── docker-compose.prod.yml   # produção (VPS)
├── deploy.sh                  # git pull + build + migrations + restart
└── .env.example
```

## Setup local

### Pré-requisitos
- Docker e Docker Compose v2

### Passos

1. Copie o arquivo de variáveis de ambiente e preencha as chaves:
   ```bash
   cp .env.example .env
   ```
   Preencha `ANTHROPIC_API_KEY`, `API_FOOTBALL_KEY`, `ODDS_API_KEY` e uma senha forte para `POSTGRES_PASSWORD` (lembre de refletir a mesma senha em `DATABASE_URL`).

2. Suba os serviços:
   ```bash
   docker compose up --build
   ```

3. Aplique as migrations do banco (em outro terminal, com os containers no ar):
   ```bash
   docker compose exec backend alembic upgrade head
   ```

4. Acesse:
   - Backend: http://localhost:8000/health
   - Frontend: http://localhost:3000

### Desenvolvimento sem Docker (opcional)

**Backend:**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Testes

```bash
cd backend
pytest
```

## Deploy na VPS Oracle ARM64 (Ubuntu)

Pressupostos desta seção (já configurados na VPS, não são repetidos aqui):
- Docker e Docker Compose v2 (plugin `docker compose`) já instalados.
- Nginx Proxy Manager (NPM) já rodando via Docker, cuidando do HTTPS/Let's Encrypt.
- As imagens usadas (`python:3.12-slim`, `node:20-alpine`, `postgres:16-alpine`, `redis:7-alpine`) são multi-arch e já têm build oficial para `linux/arm64` — nenhuma alteração de imagem é necessária.

Esta seção usa `docker-compose.prod.yml` (não o `docker-compose.yml` de desenvolvimento): sem bind-mount do código, `restart: always`, healthchecks, e sem portas publicadas no host — backend e frontend ficam acessíveis ao NPM apenas via a rede Docker compartilhada.

### 1. Clonar o repositório e configurar o `.env`

```bash
sudo mkdir -p /opt/betanalyzer
cd /opt/betanalyzer
git clone <url-do-repo> app
cd app
cp .env.example .env
```

Edite o `.env` e preencha **todas** as variáveis abaixo (veja `.env.example` para a lista completa e comentários):

| Variável | Descrição |
|---|---|
| `ANTHROPIC_API_KEY`, `API_FOOTBALL_KEY`, `ODDS_API_KEY` | Chaves de API externas |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | Credenciais do banco — use uma senha forte e única |
| `DATABASE_URL` | Deve refletir a mesma senha/usuário/db acima, host `postgres` |
| `REDIS_URL` | `redis://redis:6379/0` (padrão, não precisa mudar) |
| `NEXT_PUBLIC_API_URL` | URL pública da API, ex.: `https://api.seudominio.com` |
| `CORS_ORIGINS` | `["https://app.seudominio.com"]` — **nunca** deixe `*` em produção |
| `JWT_SECRET_KEY` | Chave forte e aleatória — gere com `openssl rand -hex 32`, nunca reuse o valor de dev |
| `REFRESH_COOKIE_SECURE` | `true` em produção (HTTPS sempre via NPM) |
| `ADMIN_EMAIL`, `ADMIN_PASSWORD` | Credenciais do usuário admin criado automaticamente no primeiro start |
| `ENVIRONMENT` | `production` |
| `NPM_NETWORK_NAME` | Nome da rede Docker externa do NPM (passo 3) |

### 2. Liberar as portas 80/443

HTTPS é servido pelo NPM, mas ele só recebe tráfego se as portas estiverem realmente abertas em **dois lugares** (é fácil esquecer o segundo na Oracle Cloud):

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw status
```

E também na **Security List** do painel Oracle Cloud (Networking → Virtual Cloud Networks → sua VCN → Security Lists → Add Ingress Rule, para `0.0.0.0/0`, portas `80` e `443`, protocolo TCP). Sem essa segunda liberação, o UFW pode estar correto e o tráfego ainda não chega à VPS — é o ponto mais comum de "funciona localmente mas não de fora".

### 3. Conectar o BetAnalyzer à rede do Nginx Proxy Manager

Para o NPM enxergar os containers `backend`/`frontend` pelo nome (sem expor portas no host), eles precisam compartilhar uma rede Docker com o NPM:

```bash
docker network ls               # localize a rede do NPM (ex.: "npm_default" ou "npm_network")
docker inspect <container_do_npm> --format '{{json .NetworkSettings.Networks}}'
```

Edite `NPM_NETWORK_NAME` no `.env` com o nome encontrado. Se a rede ainda não existir como `external` (por exemplo, se o NPM foi criado sem rede nomeada), crie-a e reaponte o NPM para ela:

```bash
docker network create npm_network
# adicione "npm_network" como rede external no docker-compose do NPM e recrie-o
```

### 4. Subir os serviços e aplicar as migrations

Use o script `deploy.sh` (faz `git pull`, build, sobe os serviços na ordem certa — Postgres/Redis primeiro, migrations, só então a API — e aguarda os healthchecks):

```bash
chmod +x deploy.sh
./deploy.sh
```

O seed do usuário admin (a partir de `ADMIN_EMAIL`/`ADMIN_PASSWORD`) acontece automaticamente no startup do backend e é idempotente — só cria o usuário se ele ainda não existir.

### 5. Configurar os Proxy Hosts no Nginx Proxy Manager

Na UI do NPM (geralmente `http://<ip-da-vps>:81`), crie dois **Proxy Hosts**:

**Frontend** (`app.seudominio.com`):
- Forward Hostname/IP: `frontend` (nome do serviço no compose — funciona porque ele está na mesma rede Docker do NPM)
- Forward Port: `3000`
- Habilite "Websockets Support" (Next.js HMR/streaming)
- Aba SSL: "Request a new SSL Certificate" (Let's Encrypt), habilite "Force SSL"

**Backend** (`api.seudominio.com`):
- Forward Hostname/IP: `backend`
- Forward Port: `8000`
- Aba SSL: igual ao frontend

Não é necessário instalar Nginx ou Certbot manualmente no host — o NPM já cuida disso. Garanta que `NEXT_PUBLIC_API_URL` no `.env` aponte para a URL pública configurada aqui (`https://api.seudominio.com`) e rode `./deploy.sh` novamente se precisar alterar essa variável (o frontend é build-time, não runtime).

### 6. Backup diário do PostgreSQL

```bash
sudo mkdir -p /opt/betanalyzer/backups
chmod +x scripts/pg_backup.sh
crontab -e
```

Adicione a linha (executa todo dia às 03:00, com retenção de 14 dias, dump comprimido em `/opt/betanalyzer/backups/`):

```cron
0 3 * * * BETANALYZER_REPO_DIR=/opt/betanalyzer/app /opt/betanalyzer/app/scripts/pg_backup.sh >> /opt/betanalyzer/backups/pg_backup.log 2>&1
```

Teste manualmente antes de confiar no cron:

```bash
BETANALYZER_REPO_DIR=/opt/betanalyzer/app ./scripts/pg_backup.sh
ls -lh /opt/betanalyzer/backups
```

### 7. Checklist de segurança antes de ir ao ar

- [ ] `JWT_SECRET_KEY` é um valor forte e aleatório (`openssl rand -hex 32`), **diferente** do default de desenvolvimento — um secret fraco permite forjar tokens de acesso.
- [ ] `CORS_ORIGINS` lista **apenas** o(s) domínio(s) reais do frontend (ex.: `["https://app.seudominio.com"]`), nunca `["*"]` — a API usa `allow_credentials=True`, e CORS aberto combinado com credenciais expõe a API a qualquer site.
- [ ] `REFRESH_COOKIE_SECURE=true` — sem isso, o cookie httpOnly do refresh token poderia ser enviado em texto puro caso algum tráfego escape do HTTPS.
- [ ] `ENVIRONMENT=production` no `.env`; o `uvicorn` em `backend/Dockerfile` já roda sem `--reload` (não recarrega/expõe stack traces de debug).
- [ ] `POSTGRES_PASSWORD` forte e exclusiva deste ambiente (não reaproveitada de dev).
- [ ] Postgres e Redis **não** têm portas publicadas no host em `docker-compose.prod.yml` — só acessíveis pela rede interna do Compose.
- [ ] Backend e frontend também sem portas publicadas no host — só alcançáveis pelo NPM via rede Docker compartilhada.
- [ ] Portas 80/443 liberadas no UFW **e** na Security List da Oracle Cloud (passo 2) — só essas duas, nada além.
- [ ] `.env` de produção nunca commitado (confirme que está no `.gitignore`) e com permissões restritas (`chmod 600 .env`).
- [ ] `ADMIN_PASSWORD` forte; após o primeiro login, considerar trocar a senha pela própria aplicação caso essa funcionalidade exista, ou recriar o usuário com nova senha se necessário.

### Atualizações futuras

```bash
cd /opt/betanalyzer/app
./deploy.sh
```

O script já faz `git pull`, rebuild, migrations e restart na ordem correta.

## Filosofia do sistema

- O objetivo é identificar **valor (EV+)**, não maximizar taxa de acerto.
- A margem da casa (overround) é sempre removida antes de comparar probabilidades.
- Toda recomendação exibe: probabilidade estimada, probabilidade implícita, EV, nível de confiança e stake sugerido (Kelly fracionado, máx. 25% do Kelly).
- Métricas de acompanhamento: ROI, EV médio, CLV (closing line value) e yield.
