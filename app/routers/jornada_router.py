from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.jornada_schema import JornadaOut
from app.services.jornada_service import (
    get_or_create_jornada_activa, listar_jornadas, cerrar_jornada, dashboard_jornada
    )
from app.database import get_db
from app.services.jornada_service import abrir_jornada_hoy, obtener_jornada_activa, cerrar_jornada

router = APIRouter(prefix="/jornadas", tags=["Jornadas"])

@router.post("/abrir")
def abrir(db: Session = Depends(get_db)):
    return abrir_jornada_hoy(db)

@router.get("/activa", response_model=JornadaOut)
def get_activa(db: Session = Depends(get_db)):
    return get_or_create_jornada_activa(db)

@router.post("/{jornada_id}/cerrar")
def cerrar(jornada_id: str, db: Session = Depends(get_db)):
    return cerrar_jornada(db, jornada_id)

@router.get("", response_model=list[JornadaOut])
def get_jornadas(estado: str | None = None, limit: int = 50, offset: int = 0, db: Session = Depends(get_db)):
    return listar_jornadas(db, estado=estado, limit=limit, offset=offset)

@router.post("/{jornada_id}/cerrar", response_model=JornadaOut)
def post_cerrar(jornada_id: str, db: Session = Depends(get_db)):
    return cerrar_jornada(db, jornada_id)

@router.get("/{jornada_id}/dashboard")
def get_dashboard(jornada_id: str, db: Session = Depends(get_db)):
    return dashboard_jornada(db, jornada_id)