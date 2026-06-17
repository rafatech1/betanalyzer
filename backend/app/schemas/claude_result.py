from pydantic import BaseModel, field_validator

from app.models.analysis import NivelConfianca

MAX_RESUMO_WORDS = 150


class ClaudeAnalysisResult(BaseModel):
    ajuste_probabilidades: dict[str, float] = {}
    justificativa: str
    riscos: list[str] = []
    confianca: NivelConfianca
    resumo: str

    @field_validator("resumo")
    @classmethod
    def _truncate_resumo(cls, value: str) -> str:
        words = value.split()
        if len(words) <= MAX_RESUMO_WORDS:
            return value
        return " ".join(words[:MAX_RESUMO_WORDS]) + "..."
