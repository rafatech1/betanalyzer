from datetime import datetime, timezone

from app.schemas.analysis_context import AnalysisContext, OddsContext
from app.services.analysis.claude_client import build_user_prompt


def _context(**overrides) -> AnalysisContext:
    base = dict(
        fixture_id=1,
        time_casa="Flamengo",
        time_fora="Palmeiras",
        data_hora=datetime(2026, 6, 20, 19, 0, tzinfo=timezone.utc),
        liga="Brasileirão",
        prob_modelo={"casa": 0.45, "empate": 0.27, "fora": 0.28},
        odds=[
            OddsContext(
                mercado="1x2", selecao="casa", odd=2.10, prob_implicita=0.46, casa_de_aposta="Betano"
            )
        ],
    )
    base.update(overrides)
    return AnalysisContext(**base)


def test_prompt_includes_team_names_and_league() -> None:
    prompt = build_user_prompt(_context())

    assert "Flamengo" in prompt
    assert "Palmeiras" in prompt
    assert "Brasileirão" in prompt


def test_prompt_includes_model_probabilities() -> None:
    prompt = build_user_prompt(_context())

    assert "45.0%" in prompt


def test_prompt_handles_missing_optional_fields_gracefully() -> None:
    prompt = build_user_prompt(_context(forma_casa=None, lesoes_casa=[], h2h_resumo=None))

    assert "sem dados" in prompt
    assert "nenhuma informada" in prompt


def test_prompt_lists_injuries_when_present() -> None:
    prompt = build_user_prompt(_context(lesoes_casa=["Jogador X (lesionado)"]))

    assert "Jogador X (lesionado)" in prompt
