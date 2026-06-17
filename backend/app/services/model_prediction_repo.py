from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fixture import Fixture, FixtureStatus
from app.models.model_prediction import ModelPrediction
from app.services.analysis.dixon_coles import MatchProbabilities

_MARKET_1X2 = "1x2"
_MARKET_OVER_UNDER = "over_under_2.5"


async def save_model_predictions(
    db: AsyncSession, fixture_id: int, probabilities: MatchProbabilities
) -> list[ModelPrediction]:
    """Registra a previsão bruta da Camada 1 (antes do ajuste do Claude) para
    acompanhamento de calibração via Brier score."""
    rows = [
        ModelPrediction(
            fixture_id=fixture_id, mercado=_MARKET_1X2, selecao="casa",
            prob_estimada=probabilities.prob_casa,
        ),
        ModelPrediction(
            fixture_id=fixture_id, mercado=_MARKET_1X2, selecao="empate",
            prob_estimada=probabilities.prob_empate,
        ),
        ModelPrediction(
            fixture_id=fixture_id, mercado=_MARKET_1X2, selecao="fora",
            prob_estimada=probabilities.prob_fora,
        ),
        ModelPrediction(
            fixture_id=fixture_id, mercado=_MARKET_OVER_UNDER, selecao="mais_2.5",
            prob_estimada=probabilities.prob_over_2_5,
        ),
        ModelPrediction(
            fixture_id=fixture_id, mercado=_MARKET_OVER_UNDER, selecao="menos_2.5",
            prob_estimada=probabilities.prob_under_2_5,
        ),
    ]
    db.add_all(rows)
    await db.commit()
    return rows


def _actual_outcome(mercado: str, selecao: str, placar_casa: int, placar_fora: int) -> bool:
    if mercado == _MARKET_1X2:
        if placar_casa > placar_fora:
            resultado = "casa"
        elif placar_casa < placar_fora:
            resultado = "fora"
        else:
            resultado = "empate"
        return selecao == resultado

    if mercado == _MARKET_OVER_UNDER:
        resultado = "mais_2.5" if (placar_casa + placar_fora) >= 3 else "menos_2.5"
        return selecao == resultado

    raise ValueError(f"mercado desconhecido: {mercado}")


async def backfill_model_prediction_results(db: AsyncSession) -> int:
    """Preenche `resultado_real` das previsões cujo fixture já terminou.
    Retorna a quantidade de linhas atualizadas."""
    stmt = (
        select(ModelPrediction, Fixture)
        .join(Fixture, ModelPrediction.fixture_id == Fixture.id)
        .where(
            ModelPrediction.resultado_real.is_(None),
            Fixture.status == FixtureStatus.FINALIZADA,
            Fixture.placar_casa.is_not(None),
            Fixture.placar_fora.is_not(None),
        )
    )

    result = await db.execute(stmt)
    rows = result.all()

    for prediction, fixture in rows:
        prediction.resultado_real = _actual_outcome(
            prediction.mercado, prediction.selecao, fixture.placar_casa, fixture.placar_fora
        )

    if rows:
        await db.commit()

    return len(rows)
