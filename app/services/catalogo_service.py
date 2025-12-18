from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException
from app.models.tipo_sopa import TipoSopa

def listar_tipos(db: Session):
    return db.execute(select(TipoSopa).order_by(TipoSopa.codigo.asc())).scalars().all()

def get_por_codigo(db: Session, codigo: str) -> TipoSopa:
    tipo = db.execute(select(TipoSopa).where(TipoSopa.codigo == codigo)).scalar_one_or_none()
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo de sopa no existe")
    return tipo

def actualizar_precio(db: Session, codigo: str, precio: float) -> TipoSopa:
    if precio <= 0:
        raise HTTPException(status_code=400, detail="El precio debe ser mayor que 0")
    tipo = get_por_codigo(db, codigo)
    tipo.precio = precio
    db.commit()
    db.refresh(tipo)
    return tipo
