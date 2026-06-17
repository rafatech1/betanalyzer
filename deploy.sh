#!/usr/bin/env bash
# Deploy/atualização do BetAnalyzer em produção (VPS Oracle ARM64).
# Uso: ./deploy.sh   (a partir da raiz do repositório clonado na VPS)
set -euo pipefail

cd "$(dirname "$0")"

COMPOSE="docker compose -f docker-compose.prod.yml"

if [ ! -f .env ]; then
  echo "Erro: arquivo .env não encontrado. Copie .env.example para .env e preencha as variáveis antes de rodar o deploy." >&2
  exit 1
fi

echo "==> Atualizando código (git pull)"
git pull

echo "==> Build das imagens"
$COMPOSE build

echo "==> Subindo postgres e redis"
$COMPOSE up -d postgres redis

echo "==> Aguardando postgres/redis ficarem saudáveis"
for svc in postgres redis; do
  for i in $(seq 1 30); do
    status="$(docker inspect --format='{{.State.Health.Status}}' "$($COMPOSE ps -q "$svc")" 2>/dev/null || echo "starting")"
    [ "$status" = "healthy" ] && break
    sleep 2
  done
done

# Aplica as migrations num container avulso, ANTES de iniciar a API.
# Isso evita que o seed do admin (executado no lifespan da app, a cada
# startup) rode contra um banco sem a tabela `users` ainda criada.
echo "==> Aplicando migrations (alembic upgrade head)"
$COMPOSE run --rm backend alembic upgrade head

echo "==> Subindo backend e frontend"
$COMPOSE up -d backend frontend

echo "==> Aguardando backend ficar saudável"
for i in $(seq 1 30); do
  status="$(docker inspect --format='{{.State.Health.Status}}' "$($COMPOSE ps -q backend)" 2>/dev/null || echo "starting")"
  [ "$status" = "healthy" ] && break
  sleep 2
done

echo "==> Deploy concluído (o seed do admin, se necessário, ocorre automaticamente no startup do backend)"
$COMPOSE ps
