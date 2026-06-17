from pydantic import BaseModel, field_validator


class LoginRequest(BaseModel):
    email: str
    senha: str


class RegisterRequest(BaseModel):
    nome: str
    email: str
    senha: str

    @field_validator("senha")
    @classmethod
    def _senha_min_length(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("A senha deve ter no mínimo 8 caracteres")
        return value


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    senha: str

    @field_validator("senha")
    @classmethod
    def _senha_min_length(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("A senha deve ter no mínimo 8 caracteres")
        return value


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
