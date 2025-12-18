from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.tipo_sopa import TipoSopaOut, TipoSopaUpdatePrice
from app.services.catalogo_service import listar_tipos, actualizar_precio

router = APIRouter(prefix="/catalogo", tags=["catalogo"])

@router.get("/tipos-sopa", response_model=list[TipoSopaOut])
def get_tipos(db: Session = Depends(get_db)):
    return listar_tipos(db)

@router.put("/tipos-sopa/{codigo}/precio", response_model=TipoSopaOut)
def put_precio(codigo: str, payload: TipoSopaUpdatePrice, db: Session = Depends(get_db)):
    return actualizar_precio(db, codigo, payload.precio)
