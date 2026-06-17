from datetime import datetime

from pydantic import BaseModel


class OddsContext(BaseModel):
    mercado: str
    selecao: str
    odd: float
    prob_implicita: float
    casa_de_aposta: str


class AnalysisContext(BaseModel):
    fixture_id: int
    time_casa: str
    time_fora: str
    data_hora: datetime
    liga: str
    prob_modelo: dict[str, float]
    odds: list[OddsContext]
    forma_casa: str | None = None
    forma_fora: str | None = None
    h2h_resumo: str | None = None
    lesoes_casa: list[str] = []
    lesoes_fora: list[str] = []
    contexto_adicional: str | None = None
    # False quando a liga não tem histórico suficiente para o modelo
    # Dixon-Coles (Camada 1) — nesse caso `prob_modelo` vem da probabilidade
    # implícita das odds (sem overround), não de um modelo ajustado, e o
    # Claude deve estimar a probabilidade diretamente em vez de só refinar.
    modelo_estatistico_disponivel: bool = True
