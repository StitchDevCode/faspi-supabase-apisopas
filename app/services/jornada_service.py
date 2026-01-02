from datetime import date, datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select, func, case
from fastapi import HTTPException

from app.models.jornada import Jornada
from app.models.pedido import Pedido

VALID_ESTADO_PEDIDO = {"PENDIENTE", "ENTREGADO", "CANCELADO"}

def obtener_jornada_activa(db: Session) -> Jornada:
    j = db.execute(
        select(Jornada).where(Jornada.estado == "ABIERTA")
    ).scalars().first()

    if not j:
        raise HTTPException(status_code=404, detail="No hay jornada activa. Abra una jornada primero.")
    return j

def abrir_jornada_hoy(db: Session) -> Jornada:
    hoy = date.today()

    # Si ya existe jornada hoy, devolverla
    existente = db.execute(
        select(Jornada).where(Jornada.fecha == hoy)
    ).scalars().first()

    if existente:
        # Si estaba cerrada, no la reabrimos por ahora (decisión simple)
        if existente.estado != "ABIERTA":
            raise HTTPException(status_code=400, detail="La jornada de hoy ya fue cerrada.")
        return existente

    # Cerrar cualquier jornada abierta anterior (por seguridad)
    abierta = db.execute(select(Jornada).where(Jornada.estado == "ABIERTA")).scalars().first()
    if abierta:
        abierta.estado = "CERRADA"
        db.add(abierta)

    j = Jornada(fecha=hoy, estado="ABIERTA")
    db.add(j)
    db.commit()
    db.refresh(j)
    return j

def cerrar_jornada(db: Session, jornada_id: str) -> Jornada:
    j = db.get(Jornada, jornada_id)
    if not j:
        raise HTTPException(status_code=404, detail="Jornada no existe")

    if j.estado != "ABIERTA":
        raise HTTPException(status_code=400, detail="La jornada ya está cerrada")

    # 1) Cancelar pendientes
    pendientes = db.execute(
        select(Pedido).where(Pedido.jornada_id == j.id, Pedido.estado == "PENDIENTE")
    ).scalars().all()

    for p in pendientes:
        p.estado = "CANCELADO"

    cancelados = len(pendientes)

    # 2) Calcular snapshot (total pedidos y recaudado solo entregados)
    # Recaudado: suma total de ENTREGADO
    total_pedidos = db.execute(
        select(func.count(Pedido.id)).where(Pedido.jornada_id == j.id)
    ).scalar_one()

    total_recaudado = db.execute(
        select(func.coalesce(func.sum(Pedido.total), 0.0)).where(
            Pedido.jornada_id == j.id,
            Pedido.estado == "ENTREGADO"
        )
    ).scalar_one()

    total_efectivo = db.execute(
        select(func.coalesce(func.sum(Pedido.total), 0.0)).where(
            Pedido.jornada_id == j.id,
            Pedido.estado == "ENTREGADO",
            Pedido.metodo_pago == "EFECTIVO"
        )
    ).scalar_one()

    total_transferencia = db.execute(
        select(func.coalesce(func.sum(Pedido.total), 0.0)).where(
            Pedido.jornada_id == j.id,
            Pedido.estado == "ENTREGADO",
            Pedido.metodo_pago == "TRANSFERENCIA"
        )
    ).scalar_one()

    # 3) Guardar snapshot y cerrar
    from datetime import datetime, timezone
    j.estado = "CERRADA"
    j.closed_at = datetime.now(timezone.utc)

    j.total_pedidos = int(total_pedidos or 0)
    j.total_recaudado = float(total_recaudado or 0.0)
    j.total_efectivo = float(total_efectivo or 0.0)
    j.total_transferencia = float(total_transferencia or 0.0)
    j.cancelados_al_cierre = cancelados

    db.add(j)
    db.commit()
    db.refresh(j)
    return j

def hoy_fecha_local() -> date:
    # Si quieres, luego lo cambiamos a “domingo actual”
    return datetime.now().date()  

def get_or_create_jornada_activa(db: Session) -> Jornada:
    j = db.execute(
        select(Jornada).where(Jornada.estado == "ACTIVA").order_by(Jornada.created_at.desc())
    ).scalars().first()

    if j:
        return j

    nueva = Jornada(fecha=hoy_fecha_local(), estado="ACTIVA")
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

def listar_jornadas(db: Session, estado: str | None = None, limit: int = 50, offset: int = 0):
    q = select(Jornada).order_by(Jornada.created_at.desc())
    if estado:
        q = q.where(Jornada.estado == estado)
    return db.execute(q.limit(limit).offset(offset)).scalars().all()

def dashboard_jornada(db: Session, jornada_id: str):
    # Ejemplos básicos (puedes ampliarlo)
    base = select(Pedido).where(Pedido.jornada_id == jornada_id, Pedido.is_deleted == False)

    total_pedidos = db.execute(select(func.count()).select_from(base.subquery())).scalar() or 0

    total_recaudado = db.execute(
        select(func.coalesce(func.sum(Pedido.total), 0.0)).where(
            Pedido.jornada_id == jornada_id,
            Pedido.is_deleted == False,
            Pedido.estado == "ENTREGADO"
        )
    ).scalar() or 0.0

    pendientes = db.execute(
        select(func.count()).select_from(Pedido).where(
            Pedido.jornada_id == jornada_id, Pedido.estado == "PENDIENTE", Pedido.is_deleted == False
        )
    ).scalar() or 0

    entregados = db.execute(
        select(func.count()).select_from(Pedido).where(
            Pedido.jornada_id == jornada_id, Pedido.estado == "ENTREGADO", Pedido.is_deleted == False
        )
    ).scalar() or 0

    cancelados = db.execute(
        select(func.count()).select_from(Pedido).where(
            Pedido.jornada_id == jornada_id, Pedido.estado == "CANCELADO", Pedido.is_deleted == False
        )
    ).scalar() or 0

    return {
        "jornada_id": jornada_id,
        "total_pedidos": total_pedidos,
        "total_recaudado": float(total_recaudado),
        "pendientes": pendientes,
        "entregados": entregados,
        "cancelados": cancelados,
    }