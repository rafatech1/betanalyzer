from anthropic import AsyncAnthropic

from app.core.config import get_settings
from app.core.logging import get_logger
from app.models.analysis import NivelConfianca
from app.schemas.analysis_context import AnalysisContext
from app.schemas.claude_result import ClaudeAnalysisResult

logger = get_logger(__name__)

CLAUDE_MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 1200

SYSTEM_PROMPT = """Você é um analista quantitativo de apostas esportivas de futebol, atuando \
como camada qualitativa sobre um modelo estatístico Dixon-Coles já calculado.

Seu papel é refinar — não substituir ingenuamente — as probabilidades do modelo, \
incorporando fatores que ele não captura: lesões, suspensões, contexto de calendário, \
motivação (decisão, rebaixamento) e padrões de confrontos diretos.

Regras importantes:
- Seja conservador. Só sugira ajustes relevantes quando houver justificativa qualitativa \
concreta nos dados fornecidos. Na ausência de sinal qualitativo forte, mantenha as \
probabilidades do modelo estatístico.
- Nunca prometa ou implique um resultado garantido. Apostas envolvem incerteza e risco de \
perda de capital.
- O resumo deve ter no máximo 150 palavras, em português, e mencionar explicitamente o EV \
e a incerteza envolvida — não apenas uma previsão de resultado.
- Sempre que possível, aponte riscos concretos (ex.: desfalques importantes, jogo sem \
motivação, viagem longa, mando de campo neutro)."""

# Acrescentado ao SYSTEM_PROMPT quando a liga não tem histórico suficiente
# para o modelo Dixon-Coles (Camada 1) — Claude passa a ser a única fonte de
# probabilidade, não apenas um refinamento sobre um modelo já ajustado.
FALLBACK_SYSTEM_ADDENDUM = """

ATENÇÃO — não há modelo estatístico ajustado para este jogo (histórico insuficiente de \
jogos da liga). As "probabilidades" fornecidas abaixo são apenas a probabilidade implícita \
das odds (sem a margem da casa) — um ponto de partida ingênuo do mercado, não uma estimativa \
de um modelo ajustado. Você deve estimar a probabilidade real de cada resultado usando seu \
conhecimento geral de futebol (força relativa dos times, rankings, fase da competição, \
contexto de calendário, motivação etc.), preenchendo `ajuste_probabilidades` com sua \
estimativa completa para todas as seleções relevantes — não apenas ajustes incrementais."""

# Inserido no início do resumo quando o fallback é usado — garante o aviso
# independentemente do que o texto gerado pelo Claude diga (item 5 do
# requisito: o resumo deve mencionar a falta de histórico do modelo).
FALLBACK_RESUMO_DISCLAIMER = (
    "Modelo estatístico sem histórico suficiente para esta liga; "
    "estimativa baseada apenas em análise qualitativa."
)


def _format_odds(context: AnalysisContext) -> str:
    if not context.odds:
        return "Nenhuma odd disponível no momento."
    return "\n".join(
        f"- {o.mercado} / {o.selecao}: odd {o.odd:.2f} ({o.casa_de_aposta}), "
        f"prob. implícita {o.prob_implicita:.1%}"
        for o in context.odds
    )


def _format_list(items: list[str], empty_label: str) -> str:
    return "\n".join(f"- {item}" for item in items) if items else empty_label


def build_user_prompt(context: AnalysisContext) -> str:
    prob_modelo = "\n".join(
        f"- {selecao}: {prob:.1%}" for selecao, prob in context.prob_modelo.items()
    )

    if context.modelo_estatistico_disponivel:
        prob_label = "Probabilidades do modelo estatístico (Dixon-Coles):"
    else:
        prob_label = (
            "Probabilidades implícitas das odds — SEM modelo estatístico ajustado "
            "(histórico insuficiente da liga), use apenas como ponto de partida:"
        )

    return f"""Jogo: {context.time_casa} (casa) x {context.time_fora} (fora)
Liga: {context.liga}
Data/hora: {context.data_hora.isoformat()}

{prob_label}
{prob_modelo}

Odds disponíveis e probabilidades implícitas (sem margem da casa):
{_format_odds(context)}

Forma recente do time da casa: {context.forma_casa or "sem dados"}
Forma recente do time visitante: {context.forma_fora or "sem dados"}

Histórico de confrontos diretos (H2H): {context.h2h_resumo or "sem dados"}

Lesões/suspensões — {context.time_casa}:
{_format_list(context.lesoes_casa, "nenhuma informada")}

Lesões/suspensões — {context.time_fora}:
{_format_list(context.lesoes_fora, "nenhuma informada")}

Contexto adicional: {context.contexto_adicional or "nenhum informado"}

Avalie esses dados e envie sua análise estruturada pela ferramenta `submit_analysis`."""


ANALYSIS_TOOL = {
    "name": "submit_analysis",
    "description": (
        "Envia o resultado estruturado da análise qualitativa do jogo: ajuste sugerido "
        "às probabilidades do modelo estatístico (com justificativa), riscos identificados, "
        "nível de confiança e um resumo em português de até 150 palavras."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "ajuste_probabilidades": {
                "type": "object",
                "description": (
                    "Probabilidade final sugerida (0 a 1) para as seleções que devem ser "
                    "ajustadas em relação ao modelo estatístico. Inclua apenas as seleções "
                    "cujo ajuste tenha justificativa qualitativa concreta; omita as demais."
                ),
                "properties": {
                    "casa": {"type": "number", "minimum": 0, "maximum": 1},
                    "empate": {"type": "number", "minimum": 0, "maximum": 1},
                    "fora": {"type": "number", "minimum": 0, "maximum": 1},
                    "mais_2.5": {"type": "number", "minimum": 0, "maximum": 1},
                    "menos_2.5": {"type": "number", "minimum": 0, "maximum": 1},
                },
            },
            "justificativa": {
                "type": "string",
                "description": "Por que os ajustes (ou a ausência deles) foram propostos.",
            },
            "riscos": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Riscos concretos identificados para esta análise.",
            },
            "confianca": {
                "type": "string",
                "enum": ["baixa", "media", "alta"],
                "description": "Nível de confiança da análise qualitativa.",
            },
            "resumo": {
                "type": "string",
                "description": "Resumo em português, até 150 palavras, mencionando EV e incerteza.",
            },
        },
        "required": ["justificativa", "confianca", "resumo"],
    },
}


async def analyze_with_claude(context: AnalysisContext) -> ClaudeAnalysisResult:
    settings = get_settings()
    client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    system_prompt = SYSTEM_PROMPT
    if not context.modelo_estatistico_disponivel:
        system_prompt += FALLBACK_SYSTEM_ADDENDUM

    message = await client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=MAX_TOKENS,
        system=system_prompt,
        tools=[ANALYSIS_TOOL],
        tool_choice={"type": "tool", "name": "submit_analysis"},
        messages=[{"role": "user", "content": build_user_prompt(context)}],
    )

    tool_use_block = next(
        (block for block in message.content if block.type == "tool_use"), None
    )
    if tool_use_block is None:
        logger.error("claude_no_tool_use_block", fixture_id=context.fixture_id)
        raise ValueError("Claude não retornou um bloco tool_use com a análise estruturada")

    result = ClaudeAnalysisResult.model_validate(tool_use_block.input)

    if not context.modelo_estatistico_disponivel:
        result = result.model_copy(
            update={
                "confianca": NivelConfianca.BAIXA,
                "resumo": f"{FALLBACK_RESUMO_DISCLAIMER} {result.resumo}",
            }
        )

    return result
