from pydantic import BaseModel
from datetime import datetime

class TipoSopaOut(BaseModel):
    id: str
    codigo: str
    nombre: str
    precio: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TipoSopaCreate(BaseModel):
    codigo: str
    nombre: str
    precio: float

class TipoSopaUpdatePrice(BaseModel):
    precio: float
