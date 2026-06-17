from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


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

    # Limites dos planos gratuitos — respeitados via contadores no Redis.
    api_football_daily_limit: int = 100
    odds_api_monthly_limit: int = 500

    odds_api_regions: str = "eu"
    odds_api_preferred_bookmaker: str = "betano"
    # Chaves de esporte/liga da The Odds API (ex.: ["soccer_brazil_campeonato", "soccer_epl"]).
    odds_api_sport_keys: list[str] = []

    # IDs de ligas da API-Football a monitorar (ex.: [71, 39]). Vazio = busca global por dia.
    monitored_league_ids: list[int] = []

    cors_origins: list[str] = ["http://localhost:3000"]

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


@lru_cache
def get_settings() -> Settings:
    return Settings()
