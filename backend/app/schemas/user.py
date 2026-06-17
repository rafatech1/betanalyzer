from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.user import UserRole


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    email: str
    role: UserRole
    ativo: bool
    created_at: datetime
