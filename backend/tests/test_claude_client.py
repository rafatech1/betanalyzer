from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from app.models.analysis import NivelConfianca
from app.schemas.analysis_context import AnalysisContext, OddsContext
from app.services.analysis import claude_client
from app.services.analysis.claude_client import (
    FALLBACK_RESUMO_DISCLAIMER,
    FALLBACK_SYSTEM_ADDENDUM,
    analyze_with_claude,
    build_user_prompt,
)


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


class _FakeMessages:
    def __init__(self, tool_input: dict) -> None:
        self._tool_input = tool_input
        self.captured_kwargs: dict = {}

    async def create(self, **kwargs):
        self.captured_kwargs = kwargs
        tool_use_block = SimpleNamespace(type="tool_use", input=self._tool_input)
        return SimpleNamespace(content=[tool_use_block])


class _FakeAsyncAnthropic:
    def __init__(self, tool_input: dict) -> None:
        self.messages = _FakeMessages(tool_input)

    def __call__(self, **kwargs):
        return self


@pytest.mark.asyncio
async def test_analyze_with_claude_forces_low_confidence_and_disclaimer_when_no_model(
    monkeypatch,
) -> None:
    fake_client = _FakeAsyncAnthropic(
        {
            "ajuste_probabilidades": {"casa": 0.5, "empate": 0.3, "fora": 0.2},
            "justificativa": "Estimativa baseada em contexto geral.",
            "confianca": "alta",
            "resumo": "Resumo gerado pelo Claude.",
        }
    )
    monkeypatch.setattr(claude_client, "AsyncAnthropic", lambda **kwargs: fake_client)

    context = _context(modelo_estatistico_disponivel=False)
    result = await analyze_with_claude(context)

    assert result.confianca == NivelConfianca.BAIXA
    assert result.resumo.startswith(FALLBACK_RESUMO_DISCLAIMER)
    assert FALLBACK_SYSTEM_ADDENDUM in fake_client.messages.captured_kwargs["system"]


@pytest.mark.asyncio
async def test_analyze_with_claude_keeps_confidence_when_model_available(monkeypatch) -> None:
    fake_client = _FakeAsyncAnthropic(
        {
            "ajuste_probabilidades": {},
            "justificativa": "Sem ajuste necessário.",
            "confianca": "alta",
            "resumo": "Resumo gerado pelo Claude.",
        }
    )
    monkeypatch.setattr(claude_client, "AsyncAnthropic", lambda **kwargs: fake_client)

    result = await analyze_with_claude(_context())

    assert result.confianca == NivelConfianca.ALTA
    assert result.resumo == "Resumo gerado pelo Claude."
    assert FALLBACK_SYSTEM_ADDENDUM not in fake_client.messages.captured_kwargs["system"]
