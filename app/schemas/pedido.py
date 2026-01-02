from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PedidoCreate(BaseModel):
    client_request_id: str
    client_id: str | None = None
    cliente: str
    tipo_sopa_codigo: str
    metodo_pago: str
    cantidad: int = 1
    direccion: str
    pago_con_monto_exacto: bool = True
    monto_pagado: float = 0.0

    es_especial: bool = False
    descripcion_especial: Optional[str] = None

class PedidoUpdate(BaseModel):
    cliente: Optional[str] = None
    direccion: Optional[str] = None
    estado: Optional[str] = None
    metodo_pago: Optional[str] = None
    cantidad: Optional[int] = None
    pago_con_monto_exacto: Optional[bool] = None
    monto_pagado: Optional[float] = None
     # 👇 NUEVO
    es_especial: Optional[bool] = None
    descripcion_especial: Optional[str] = None

class PedidoOut(BaseModel):
    id: str
    jornada_id: str
    client_id: str | None = None
    client_request_id: str
    client_id: str | None
    is_deleted: bool
    deleted_at: datetime | None
    tipo_sopa_codigo: str
    metodo_pago: str
    estado: str
    cantidad: int
    direccion: str
    pago_con_monto_exacto: bool
    monto_pagado: float
    total: float
    vuelto: float
    es_especial: bool
    descripcion_especial: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class Config:
    from_attributes = True
