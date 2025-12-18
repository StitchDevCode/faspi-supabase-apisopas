from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.pedido import PedidoCreate, PedidoUpdate, PedidoOut
from app.services.pedido_service import crear_pedido, listar_pedidos, obtener_pedido, actualizar_pedido, eliminar_pedido

router = APIRouter(prefix="/pedidos", tags=["pedidos"])

@router.post("", response_model=PedidoOut, status_code=status.HTTP_201_CREATED)
def post_pedido(payload: PedidoCreate, db: Session = Depends(get_db)):
    return crear_pedido(db, payload)

@router.get("", response_model=list[PedidoOut])
def get_pedidos(db: Session = Depends(get_db)):
    return listar_pedidos(db)

@router.get("/{pedido_id}", response_model=PedidoOut)
def get_pedido(pedido_id: str, db: Session = Depends(get_db)):
    return obtener_pedido(db, pedido_id)

@router.patch("/{pedido_id}", response_model=PedidoOut)
def patch_pedido(pedido_id: str, payload: PedidoUpdate, db: Session = Depends(get_db)):
    return actualizar_pedido(db, pedido_id, payload)

@router.delete("/{pedido_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pedido(pedido_id: str, db: Session = Depends(get_db)):
    eliminar_pedido(db, pedido_id)
    return None
