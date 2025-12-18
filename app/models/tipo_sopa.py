import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

def now_utc():
    return datetime.now(timezone.utc)

class TipoSopa(Base):
    __tablename__ = "tipos_sopa"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    codigo: Mapped[str] = mapped_column(String(50), unique=True, index=True)  # CON_EMPAQUE / SIN_EMPAQUE
    nombre: Mapped[str] = mapped_column(String(120))
    precio: Mapped[float] = mapped_column(Float)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)
