from datetime import datetime, timedelta, timezone


def is_analysis_cache_valid(
    batch_created_at: datetime,
    batch_odds: dict[tuple[str, str], float],
    current_odds: dict[tuple[str, str], float],
    ttl_hours: float,
    change_threshold: float,
    now: datetime | None = None,
) -> bool:
    """Uma análise compartilhada é reaproveitável se: (1) não passou da validade
    (`ttl_hours`) e (2) nenhuma odd usada como referência se moveu mais que
    `change_threshold` (variação relativa) desde então."""
    now = now or datetime.now(timezone.utc)
    created_at = batch_created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    if now - created_at > timedelta(hours=ttl_hours):
        return False

    for key, reference_odd in batch_odds.items():
        current_odd = current_odds.get(key)
        if current_odd is None or reference_odd <= 0:
            continue

        relative_change = abs(current_odd - reference_odd) / reference_odd
        if relative_change > change_threshold:
            return False

    return True
