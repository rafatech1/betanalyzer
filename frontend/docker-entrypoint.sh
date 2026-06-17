#!/bin/sh
# Gera public/env-config.js com o valor REAL de NEXT_PUBLIC_API_URL no
# startup do container (runtime), não no build — assim a mesma imagem pode
# ser reaproveitada em ambientes diferentes (dev/staging/prod) só trocando
# a variável de ambiente, sem rebuildar.
set -e

API_URL="${NEXT_PUBLIC_API_URL:-http://localhost:8000}"

cat > ./public/env-config.js <<EOF
window.__ENV__ = {
  API_URL: "${API_URL}"
};
EOF

exec node server.js
