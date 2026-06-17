from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import get_logger
from app.models.analysis import Analysis, Recomendacao
from app.services.analysis.cache_validity import is_analysis_cache_valid
from app.services.analysis.claude_client import analyze_with_claude
from app.services.analysis.context_builder import build_analysis_context
from app.services.analysis.dixon_coles import predict_match
from app.services.analysis.ev import calculate_ev, should_recommend, suggested_stake
from app.services.analysis.exceptions import FixtureNotFoundError, InsufficientModelDataError
from app.services.analysis.lock import AnalysisInProgressError, analysis_lock
from app.services.analysis.merge import match_probabilities_to_dict, merge_probabilities
from app.services.analysis.model_cache import get_team_ratings
from app.services.analysis_repo import (
    get_latest_analysis_batch,
    get_latest_odds_by_selection,
    save_analyses,
)
from app.services.external.api_football import APIFootballClient
from app.services.fixtures_repo import get_fixture_with_relations
from app.services.model_prediction_repo import save_model_predictions
from app.services.probability import remove_overround

logger = get_logger(__name__)


def _build_prob_modelo_from_odds(odds_rows: list) -> dict[str, float]:
    """Estima probabilidades a partir das odds (sem overround) quando o
    modelo Dixon-Coles não tem histórico suficiente para a liga — apenas um
    ponto de partida ingênuo para o Claude refinar (Camada 2)."""
    rows_by_market: dict[str, list] = {}
    for row in odds_rows:
        rows_by_market.setdefault(row.mercado, []).append(row)

    prob_modelo: dict[str, float] = {}
    for rows in rows_by_market.values():
        probs = remove_overround([row.odd for row in rows])
        for row, prob in zip(rows, probs):
            prob_modelo[row.selecao] = prob

    return prob_modelo


def _check_cache(
    batch: list[Analysis], current_odds_map: dict[tuple[str, str], float]
) -> list[Analysis] | None:
    if not batch:
        return None

    settings = get_settings()
    batch_odds_map = {(row.mercado, row.selecao): row.odd_referencia for row in batch}

    if is_analysis_cache_valid(
        batch_created_at=batch[0].created_at,
        batch_odds=batch_odds_map,
        current_odds=current_odds_map,
        ttl_hours=settings.analysis_cache_ttl_hours,
        change_threshold=settings.analysis_odds_change_threshold,
    ):
        return batch

    return None


async def _run_full_pipeline(db: AsyncSession, fixture_id: int, contexto_adicional: str | None) -> list[Analysis]:
    settings = get_settings()

    fixture = await get_fixture_with_relations(db, fixture_id)
    if fixture is None:
        raise FixtureNotFoundError(f"Fixture {fixture_id} não encontrado")

    odds_rows = await get_latest_odds_by_selection(db, fixture_id)

    ratings = await get_team_ratings(db, fixture.liga_id)
    modelo_disponivel = ratings is not None

    if modelo_disponivel:
        probabilities = predict_match(ratings, fixture.time_casa_id, fixture.time_fora_id)
        await save_model_predictions(db, fixture_id, probabilities)
        model_probs = match_probabilities_to_dict(probabilities)
    elif odds_rows:
        # Sem histórico suficiente para o Dixon-Coles — usa a probabilidade
        # implícita das odds como ponto de partida e deixa o Claude (Camada 2)
        # estimar a probabilidade real (ver FALLBACK_SYSTEM_ADDENDUM).
        logger.info("analysis_fallback_claude_only", fixture_id=fixture_id, liga_id=fixture.liga_id)
        model_probs = _build_prob_modelo_from_odds(odds_rows)
    else:
        raise InsufficientModelDataError(
            f"Histórico insuficiente para ajustar o modelo estatístico da liga {fixture.liga_id} "
            "e nenhuma odd disponível para estimativa alternativa"
        )

    api_client = APIFootballClient()
    context = await build_analysis_context(
        db,
        fixture,
        model_probs,
        odds_rows,
        api_client,
        modelo_estatistico_disponivel=modelo_disponivel,
        contexto_adicional=contexto_adicional,
    )

    claude_result = await analyze_with_claude(context)

    final_probs = merge_probabilities(model_probs, claude_result.ajuste_probabilidades)

    rows: list[Analysis] = []
    for odd_row in odds_rows:
        if odd_row.selecao not in final_probs:
            continue

        prob_final = final_probs[odd_row.selecao]
        ev = calculate_ev(prob_final, odd_row.odd)

        if should_recommend(ev, claude_result.confianca, settings.ev_recommendation_threshold):
            recomendacao = Recomendacao.APOSTAR
            stake = suggested_stake(
                prob_final,
                odd_row.odd,
                settings.max_kelly_fraction,
                settings.max_stake_fraction_of_bankroll,
            )
        elif ev > 0:
            recomendacao = Recomendacao.OBSERVAR
            stake = 0.0
        else:
            recomendacao = Recomendacao.EVITAR
            stake = 0.0

        rows.append(
            Analysis(
                fixture_id=fixture_id,
                mercado=odd_row.mercado,
                selecao=odd_row.selecao,
                odd_referencia=odd_row.odd,
                prob_estimada=prob_final,
                prob_implicita=odd_row.prob_implicita,
                ev=ev,
                confianca=claude_result.confianca,
                recomendacao=recomendacao,
                stake_sugerido=stake,
                resumo_ia=claude_result.resumo,
            )
        )

    if not rows:
        logger.info("analysis_pipeline_no_odds_available", fixture_id=fixture_id)
        return []

    return await save_analyses(db, rows)


async def run_analysis_pipeline(
    db: AsyncSession, fixture_id: int, contexto_adicional: str | None = None
) -> list[Analysis]:
    """Executa o pipeline de análise completo (camada estatística + qualitativa),
    reaproveitando uma análise recente e válida quando possível (arquitetura de
    análise compartilhada) e usando lock no Redis para evitar duplicação."""
    odds_rows = await get_latest_odds_by_selection(db, fixture_id)
    current_odds_map = {(row.mercado, row.selecao): row.odd for row in odds_rows}

    existing_batch = await get_latest_analysis_batch(db, fixture_id)
    cached = _check_cache(existing_batch, current_odds_map)
    if cached is not None:
        logger.info("analysis_cache_hit", fixture_id=fixture_id)
        return cached

    try:
        async with analysis_lock(fixture_id):
            # reconfere após adquirir o lock — outra requisição pode ter
            # acabado de gerar uma análise válida enquanto esperávamos.
            existing_batch = await get_latest_analysis_batch(db, fixture_id)
            cached = _check_cache(existing_batch, current_odds_map)
            if cached is not None:
                return cached

            return await _run_full_pipeline(db, fixture_id, contexto_adicional)
    except AnalysisInProgressError:
        existing_batch = await get_latest_analysis_batch(db, fixture_id)
        if existing_batch:
            logger.info("analysis_in_progress_serving_stale_cache", fixture_id=fixture_id)
            return existing_batch
        raise
