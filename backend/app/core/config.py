import json
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _parse_cors_origins(raw: str) -> list[str]:
    # CORS_ORIGINS no .env é esperado em JSON (ex.: ["https://app.x.com"]),
    # mas aceita também uma lista separada por vírgulas como fallback.
    try:
        origins = json.loads(raw)
    except json.JSONDecodeError:
        origins = [origin.strip() for origin in raw.split(",") if origin.strip()]
    # O header `Origin` enviado pelo browser nunca tem barra final; uma
    # origem configurada com "/" no final nunca daria match e o
    # CORSMiddleware rejeitaria o preflight com 400 silenciosamente.
    return [str(origin).rstrip("/") for origin in origins]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "BetAnalyzer API"
    environment: str = "development"
    log_level: str = "INFO"

    database_url: str
    redis_url: str

    anthropic_api_key: str = ""
    api_football_key: str = ""
    odds_api_key: str = ""

    api_football_base_url: str = "https://v3.football.api-sports.io"
    odds_api_base_url: str = "https://api.the-odds-api.com/v4"

    # Temporada fixa para chamadas à API-Football (ex.: 2024). Opcional: o
    # plano gratuito não cobre a temporada atual, então quando não definida
    # o cálculo automático (current_season()) pode apontar para uma
    # temporada sem acesso. A API-Football é usada hoje só para H2H/lesões
    # (não mais para a listagem de jogos, que vem da The Odds API).
    football_season: int | None = None

    # Limites dos planos gratuitos — respeitados via contadores no Redis.
    api_football_daily_limit: int = 100
    odds_api_monthly_limit: int = 500

    odds_api_regions: str = "eu"
    odds_api_preferred_bookmaker: str = "betano"
    # Chaves de esporte/liga da The Odds API (ex.: ["soccer_brazil_campeonato", "soccer_epl"]).
    odds_api_sport_keys: list[str] = []

    # IDs de ligas da API-Football a monitorar (ex.: [71, 39]). Vazio = busca global por dia.
    monitored_league_ids: list[int] = []

    # Campo cru como string (não list[str]) de propósito: o pydantic-settings
    # tenta decodificar campos de lista lidos do .env como JSON ANTES de
    # qualquer validador rodar, e derruba a app inteira no startup se o
    # formato não for um JSON estrito — o que é fácil de errar num .env
    # (ex.: sem colchetes, ou separado só por vírgula). Mantendo como string
    # aqui, o parsing fica sob nosso controle em `cors_origins` abaixo.
    cors_origins_raw: str = Field(default='["http://localhost:3000"]', alias="cors_origins")

    @property
    def cors_origins(self) -> list[str]:
        return _parse_cors_origins(self.cors_origins_raw)

    # Kelly fracionado: nunca apostar mais que esta fração do Kelly completo.
    max_kelly_fraction: float = 0.25
    # Teto de stake sugerido, como fração da banca, independente do Kelly.
    max_stake_fraction_of_bankroll: float = 0.03
    # EV mínimo para que uma recomendação seja emitida (3% = 0.03).
    ev_recommendation_threshold: float = 0.03

    # Janela futura considerada "próxima" para atualização de odds com mais frequência.
    odds_update_window_hours: int = 48

    # Validade do cache de análises compartilhadas e variação de odds que invalida o cache.
    analysis_cache_ttl_hours: int = 6
    analysis_odds_change_threshold: float = 0.05

    # Ligas monitoradas para pré-análise automática (job diário).
    pre_analysis_league_ids: list[int] = []
    pre_analysis_window_hours: int = 24

    # Autenticação JWT.
    jwt_secret_key: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    refresh_cookie_secure: bool = False

    # Seed do usuário admin (uso pessoal, sem cadastro aberto).
    admin_email: str = ""
    admin_password: str = ""

    # Rate limiting de login (tentativas por IP).
    login_rate_limit_attempts: int = 5
    login_rate_limit_window_seconds: int = 60
    login_lockout_seconds: int = 300

    # Envio de email transacional (Resend) — usado hoje só para o fluxo de
    # "esqueci minha senha". Sem a chave configurada, o envio é apenas
    # logado (ver app/services/email.py), não falha a request.
    resend_api_key: str = ""
    resend_from_email: str = "BetAnalyzer <onboarding@resend.dev>"

    # URL pública do frontend, usada para montar o link de redefinição de
    # senha enviado por email (ex.: {FRONTEND_URL}/reset-password?token=...).
    frontend_url: str = "http://localhost:3000"

    password_reset_token_expire_hours: int = 1


@lru_cache
def get_settings() -> Settings:
    return Settings()
