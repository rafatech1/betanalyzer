from app.models.analysis import NivelConfianca
from app.schemas.claude_result import MAX_RESUMO_WORDS, ClaudeAnalysisResult


def _result(resumo: str) -> ClaudeAnalysisResult:
    return ClaudeAnalysisResult(
        justificativa="j",
        riscos=[],
        confianca=NivelConfianca.MEDIA,
        resumo=resumo,
    )


def test_short_resumo_kept_unchanged() -> None:
    result = _result("Resumo curto sem necessidade de corte.")
    assert result.resumo == "Resumo curto sem necessidade de corte."


def test_long_resumo_truncated_to_max_words() -> None:
    resumo = " ".join(f"palavra{i}" for i in range(200))
    result = _result(resumo)

    words = result.resumo.rstrip(".").split()
    assert len(words) == MAX_RESUMO_WORDS
    assert result.resumo.endswith("...")
