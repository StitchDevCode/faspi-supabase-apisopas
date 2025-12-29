import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, Boolean, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from typing import Optional

def now_utc():
    return datetime.now(timezone.utc)

class Pedido(Base):
    __tablename__ = "pedidos"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    cliente: Mapped[str] = mapped_column(String(120))
    tipo_sopa_codigo: Mapped[str] = mapped_column(String(50), index=True)   # CON_EMPAQUE / SIN_EMPAQUE
    metodo_pago: Mapped[str] = mapped_column(String(30))                    # EFECTIVO / TRANSFERENCIA
    estado: Mapped[str] = mapped_column(String(30), default="PENDIENTE")     # PENDIENTE / ENTREGADO / CANCELADO

    cantidad: Mapped[int] = mapped_column(Integer, default=1)
    direccion: Mapped[str] = mapped_column(String(250))

    pago_con_monto_exacto: Mapped[bool] = mapped_column(Boolean, default=True)
    monto_pagado: Mapped[float] = mapped_column(Float, default=0.0)

    # ⚠️ total/vuelto se calculan en backend (no confiar en cliente)
    total: Mapped[float] = mapped_column(Float, default=0.0)
    vuelto: Mapped[float] = mapped_column(Float, default=0.0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)

    client_id: Mapped[Optional[str]] = mapped_column(String(80), nullable=True, index=True)
    client_request_id: Mapped[str] = mapped_column(String(80), unique=True, index=True)

    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    es_especial: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    descripcion_especial: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
