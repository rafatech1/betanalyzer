class FixtureNotFoundError(Exception):
    """Fixture não encontrado."""


class InsufficientModelDataError(Exception):
    """Não há histórico suficiente de jogos da liga para ajustar o modelo
    estatístico com confiança mínima."""
