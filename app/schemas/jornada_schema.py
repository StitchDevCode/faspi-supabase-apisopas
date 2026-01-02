from pydantic import BaseModel
from datetime import date, datetime

class JornadaOut(BaseModel):
    id: str
    fecha: date
    estado: str
    created_at: datetime
    closed_at: datetime | None = None

    class Config:
        from_attributes = True
