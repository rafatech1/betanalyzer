from sqlalchemy.ext.asyncio import AsyncSession

from app.models.odds import Odds
from app.services.external.odds_api import OddsSelection
from app.services.probability import remove_overround


def _attach_implied_probabilities(
    selections: list[OddsSelection],
) -> list[tuple[OddsSelection, float]]:
    grouped: dict[str, list[OddsSelection]] = {}
    for selection in selections:
        grouped.setdefault(selection.mercado, []).append(selection)

    paired: list[tuple[OddsSelection, float]] = []
    for group in grouped.values():
        probabilities = remove_overround([s.odd for s in group])
        paired.extend(zip(group, probabilities))

    return paired


async def save_odds_selections(
    db: AsyncSession, fixture_id: int, selections: list[OddsSelection]
) -> list[Odds]:
    """Insere uma nova linha de histórico por seleção — nunca sobrescreve odds
    anteriores, permitindo calcular CLV (closing line value) depois."""
    rows: list[Odds] = []
    for selection, prob_implicita in _attach_implied_probabilities(selections):
        row = Odds(
            fixture_id=fixture_id,
            casa_de_aposta=selection.casa_de_aposta,
            mercado=selection.mercado,
            selecao=selection.selecao,
            odd=selection.odd,
            prob_implicita=prob_implicita,
        )
        db.add(row)
        rows.append(row)

    await db.commit()
    return rows
