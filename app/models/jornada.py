import uuid
from datetime import datetime, timezone, date
from sqlalchemy import String, Date, DateTime, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

def now_utc():
    return datetime.now(timezone.utc)

class Jornada(Base):
    __tablename__ = "jornadas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    fecha: Mapped[date] = mapped_column(Date, unique=True, index=True)  # 1 jornada por día
    estado: Mapped[str] = mapped_column(String(20), default="ABIERTA", index=True)  # ABIERTA / CERRADA

    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)   

    # Snapshot (se llena al cerrar)
    total_pedidos: Mapped[int] = mapped_column(Integer, default=0)
    total_recaudado: Mapped[float] = mapped_column(Float, default=0.0)
    total_efectivo: Mapped[float] = mapped_column(Float, default=0.0)
    total_transferencia: Mapped[float] = mapped_column(Float, default=0.0)
    cancelados_al_cierre: Mapped[int] = mapped_column(Integer, default=0)

    # Relación (opcional pero útil)
    pedidos = relationship("Pedido", back_populates="jornada")
