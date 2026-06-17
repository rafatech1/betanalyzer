from app.services.external.odds_api import OddsSelection, extract_best_odds


def _event(bookmakers: list[dict]) -> dict:
    return {
        "id": "evt1",
        "home_team": "Flamengo",
        "away_team": "Palmeiras",
        "bookmakers": bookmakers,
    }


def test_prefers_betano_odd_even_when_not_the_best() -> None:
    event = _event(
        [
            {
                "key": "betano",
                "title": "Betano",
                "markets": [
                    {
                        "key": "h2h",
                        "outcomes": [
                            {"name": "Flamengo", "price": 1.80},
                            {"name": "Draw", "price": 3.20},
                            {"name": "Palmeiras", "price": 4.50},
                        ],
                    }
                ],
            },
            {
                "key": "bet365",
                "title": "Bet365",
                "markets": [
                    {
                        "key": "h2h",
                        "outcomes": [
                            {"name": "Flamengo", "price": 1.95},
                            {"name": "Draw", "price": 3.30},
                            {"name": "Palmeiras", "price": 4.60},
                        ],
                    }
                ],
            },
        ]
    )

    result = extract_best_odds(event, preferred_bookmaker="betano")
    casa = next(r for r in result if r.mercado == "1x2" and r.selecao == "casa")

    assert casa.odd == 1.80
    assert casa.casa_de_aposta == "Betano"


def test_falls_back_to_best_odd_when_preferred_bookmaker_absent() -> None:
    event = _event(
        [
            {
                "key": "bet365",
                "title": "Bet365",
                "markets": [
                    {
                        "key": "h2h",
                        "outcomes": [
                            {"name": "Flamengo", "price": 1.95},
                            {"name": "Draw", "price": 3.30},
                            {"name": "Palmeiras", "price": 4.60},
                        ],
                    }
                ],
            },
            {
                "key": "pinnacle",
                "title": "Pinnacle",
                "markets": [
                    {
                        "key": "h2h",
                        "outcomes": [
                            {"name": "Flamengo", "price": 2.05},
                            {"name": "Draw", "price": 3.10},
                            {"name": "Palmeiras", "price": 4.40},
                        ],
                    }
                ],
            },
        ]
    )

    result = extract_best_odds(event, preferred_bookmaker="betano")
    casa = next(r for r in result if r.mercado == "1x2" and r.selecao == "casa")

    assert casa.odd == 2.05
    assert casa.casa_de_aposta == "Pinnacle"


def test_filters_totals_market_to_point_2_5_only() -> None:
    event = _event(
        [
            {
                "key": "bet365",
                "title": "Bet365",
                "markets": [
                    {
                        "key": "totals",
                        "outcomes": [
                            {"name": "Over", "price": 1.85, "point": 1.5},
                            {"name": "Under", "price": 1.95, "point": 1.5},
                            {"name": "Over", "price": 2.00, "point": 2.5},
                            {"name": "Under", "price": 1.80, "point": 2.5},
                        ],
                    }
                ],
            }
        ]
    )

    result = extract_best_odds(event, preferred_bookmaker="betano")
    selections = {r.selecao: r.odd for r in result if r.mercado == "over_under_2.5"}

    assert selections == {"mais_2.5": 2.00, "menos_2.5": 1.80}


def test_extracts_both_teams_to_score_market() -> None:
    event = _event(
        [
            {
                "key": "bet365",
                "title": "Bet365",
                "markets": [
                    {
                        "key": "btts",
                        "outcomes": [
                            {"name": "Yes", "price": 1.70},
                            {"name": "No", "price": 2.10},
                        ],
                    }
                ],
            }
        ]
    )

    result = extract_best_odds(event, preferred_bookmaker="betano")
    selections = {r.selecao: r.odd for r in result if r.mercado == "ambas_marcam"}

    assert selections == {"sim": 1.70, "nao": 2.10}
