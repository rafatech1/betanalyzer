from pydantic import BaseModel


class FixtureDetailsOut(BaseModel):
    forma_casa: str | None
    forma_fora: str | None
    h2h_resumo: str | None
    lesoes_casa: list[str]
    lesoes_fora: list[str]
