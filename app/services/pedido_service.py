from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException
from app.models.pedido import Pedido
from app.services.catalogo_service import get_por_codigo

VALID_METODO = {"EFECTIVO", "TRANSFERENCIA"}
VALID_ESTADO = {"PENDIENTE", "ENTREGADO", "CANCELADO"}

def _calcular_total_y_vuelto(tipo_precio: float, cantidad: int, pago_exacto: bool, monto_pagado: float):
    total = float(tipo_precio) * int(cantidad)
    if pago_exacto:
        return total, 0.0, total  # total, vuelto, monto_pagado_final
    if monto_pagado < total:
        raise HTTPException(status_code=400, detail="Monto pagado no puede ser menor que el total")
    vuelto = float(monto_pagado) - total
    return total, vuelto, float(monto_pagado)

def crear_pedido(db: Session, payload) -> Pedido:
    if payload.metodo_pago not in VALID_METODO:
        raise HTTPException(status_code=400, detail="MetodoPago inválido")
    if payload.cantidad <= 0:
        raise HTTPException(status_code=400, detail="Cantidad inválida")
    if payload.es_especial and not payload.descripcion_especial:
        raise HTTPException(
            status_code=400,
            detail="Descripcion especial es requerida cuando el pedido es especial"
        )

    if not payload.es_especial:
        payload.descripcion_especial = None

    tipo = get_por_codigo(db, payload.tipo_sopa_codigo)

    total, vuelto, monto_final = _calcular_total_y_vuelto(
        tipo_precio=tipo.precio,
        cantidad=payload.cantidad,
        pago_exacto=payload.pago_con_monto_exacto,
        monto_pagado=payload.monto_pagado,
    )

    pedido = Pedido(
        client_request_id=payload.client_request_id,
        client_id=payload.client_id,

        cliente=payload.cliente,
        tipo_sopa_codigo=payload.tipo_sopa_codigo,
        metodo_pago=payload.metodo_pago,
        cantidad=payload.cantidad,
        direccion=payload.direccion,
        pago_con_monto_exacto=payload.pago_con_monto_exacto,
        monto_pagado=monto_final,
        total=total,
        vuelto=vuelto,
        estado="PENDIENTE",
 

        es_especial=getattr(payload, "es_especial", False),
        descripcion_especial=getattr(payload, "descripcion_especial", None),
    )

    db.add(pedido)
    db.commit()
    db.refresh(pedido)
    return pedido

def listar_pedidos(db: Session):
    return db.execute(select(Pedido).order_by(Pedido.created_at.desc())).scalars().all()

def obtener_pedido(db: Session, pedido_id: str) -> Pedido:
    pedido = db.get(Pedido, pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no existe")
    return pedido

def actualizar_pedido(db: Session, pedido_id: str, payload) -> Pedido:
    pedido = obtener_pedido(db, pedido_id)

    data = payload.model_dump(exclude_unset=True)

    if "metodo_pago" in data and data["metodo_pago"] not in VALID_METODO:
        raise HTTPException(status_code=400, detail="MetodoPago inválido")
    if "estado" in data and data["estado"] not in VALID_ESTADO:
        raise HTTPException(status_code=400, detail="Estado inválido")
    if "cantidad" in data and data["cantidad"] <= 0:
        raise HTTPException(status_code=400, detail="Cantidad inválida")

    # aplicar cambios simples
    for k, v in data.items():
        setattr(pedido, k, v)

    # si cambió tipo/cantidad/pago, recalcular
    if any(k in data for k in ["tipo_sopa_codigo", "cantidad", "pago_con_monto_exacto", "monto_pagado"]):
        tipo = get_por_codigo(db, pedido.tipo_sopa_codigo)
        total, vuelto, monto_final = _calcular_total_y_vuelto(
            tipo_precio=tipo.precio,
            cantidad=pedido.cantidad,
            pago_exacto=pedido.pago_con_monto_exacto,
            monto_pagado=pedido.monto_pagado,
        )
        pedido.total = total
        pedido.vuelto = vuelto
        pedido.monto_pagado = monto_final
    # Reglas de especial (update)
    if "es_especial" in data or "descripcion_especial" in data:
        nuevo_es_especial = data.get("es_especial", pedido.es_especial)
        nueva_desc = data.get("descripcion_especial", pedido.descripcion_especial)

    if nuevo_es_especial and not nueva_desc:
        raise HTTPException(
            status_code=400,
            detail="Descripcion especial es requerida cuando el pedido es especial"
        )

    if not nuevo_es_especial:
        # si deja de ser especial, limpiamos la descripcion
        data["descripcion_especial"] = None

    db.commit()
    db.refresh(pedido)
    return pedido

def eliminar_pedido(db: Session, pedido_id: str):
    pedido = obtener_pedido(db, pedido_id)
    db.delete(pedido)
    db.commit()
