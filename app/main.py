from fastapi import FastAPI
from sqlalchemy.orm import Session

from app.database import Base, engine, SessionLocal
from app.models.tipo_sopa import TipoSopa

from app.routers.pedido_router import router as pedido_router
from app.routers.catalogo_router import router as catalogo_router
from app.routers.jornada_router import router as jornada_router

from app.models.pedido import Pedido
from app.models.jornada import Jornada

app = FastAPI(title="Sopas API")

def seed_catalogo():
    db: Session = SessionLocal()
    try:
        def upsert(codigo: str, nombre: str, precio: float):
            tipo = db.query(TipoSopa).filter_by(codigo=codigo).first()
            if not tipo:
                db.add(TipoSopa(codigo=codigo, nombre=nombre, precio=precio))

        upsert("CON_EMPAQUE", "Con empaque", 180.0)
        upsert("SIN_EMPAQUE", "Sin empaque", 160.0)
        db.commit()
    finally:
        db.close()

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    seed_catalogo()

@app.get("/")
def root():
    return {"message": "Sopas API OK"}

@app.get("/health")
def health():
    return {"ok": True}

app.include_router(pedido_router)
app.include_router(catalogo_router)
app.include_router(jornada_router)