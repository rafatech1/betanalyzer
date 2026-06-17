#!/usr/bin/env bash
# Backup diário comprimido do PostgreSQL do BetAnalyzer, com retenção de 14 dias.
# Pensado para rodar via cron na própria VPS (não dentro de um container).
# Veja o README ("Backup diário do PostgreSQL") para a instalação completa via cron.
set -euo pipefail

# Diretório do repositório clonado (onde está o docker-compose.prod.yml e o .env).
REPO_DIR="${BETANALYZER_REPO_DIR:-/opt/betanalyzer/app}"
BACKUP_DIR="${BETANALYZER_BACKUP_DIR:-/opt/betanalyzer/backups}"
RETENTION_DAYS=14

cd "$REPO_DIR"

# Lê só as variáveis necessárias do .env (não usa `source` porque o arquivo
# também contém valores em formato JSON como CORS_ORIGINS=["..."], que não
# são seguros de interpretar diretamente como shell).
POSTGRES_USER="$(grep -E '^POSTGRES_USER=' .env | head -n1 | cut -d= -f2-)"
POSTGRES_DB="$(grep -E '^POSTGRES_DB=' .env | head -n1 | cut -d= -f2-)"

if [ -z "$POSTGRES_USER" ] || [ -z "$POSTGRES_DB" ]; then
  echo "Erro: POSTGRES_USER/POSTGRES_DB não encontrados em $REPO_DIR/.env" >&2
  exit 1
fi

mkdir -p "$BACKUP_DIR"

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
DUMP_FILE="$BACKUP_DIR/betanalyzer_${TIMESTAMP}.sql.gz"

echo "[$(date -Iseconds)] Iniciando backup -> $DUMP_FILE"

docker compose -f docker-compose.prod.yml exec -T postgres \
  pg_dump -U "${POSTGRES_USER}" "${POSTGRES_DB}" | gzip > "$DUMP_FILE"

echo "[$(date -Iseconds)] Backup concluído: $(du -h "$DUMP_FILE" | cut -f1)"

echo "[$(date -Iseconds)] Removendo backups com mais de ${RETENTION_DAYS} dias"
find "$BACKUP_DIR" -name 'betanalyzer_*.sql.gz' -mtime "+${RETENTION_DAYS}" -print -delete

echo "[$(date -Iseconds)] Backup finalizado com sucesso"
