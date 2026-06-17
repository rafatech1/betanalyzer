// Placeholder de desenvolvimento. Em produção, este arquivo é REGERADO no
// startup do container (docker-entrypoint.sh) com o valor real de
// NEXT_PUBLIC_API_URL, permitindo trocar a URL da API sem rebuildar a imagem.
window.__ENV__ = {
  API_URL: "http://localhost:8000",
};
