from fastapi import APIRouter, HTTPException, Query
from bson import ObjectId

from crud.common import db, ensure_indexed_query
from crud.update import cambiar_estado_orden
from transactions.transactions import crear_orden_y_actualizar_puntos
from api.schemas import OrderCreate, UpdateStatusRequest

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("/")
def get_orders(
    estado: str | None = None,
    sort_by: str = Query("fecha_pedido"),
    sort_dir: int = Query(-1),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    filtro = {}
    if estado:
        filtro["estado"] = estado
    ensure_indexed_query(db.ordenes, filtro)
    sort_direction = 1 if sort_dir >= 0 else -1
    ordenes = list(
        db.ordenes.find(
            filtro,
            {
                "usuario_id": 1,
                "restaurante_id": 1,
                "estado": 1,
                "fecha_pedido": 1,
                "total": 1,
            },
        ).sort(sort_by, sort_direction).skip(skip).limit(limit)
    )

    for o in ordenes:
        usuario = db.usuarios.find_one({"_id": o.get("usuario_id")}, {"nombre": 1, "apellido": 1})
        restaurante = db.restaurantes.find_one({"_id": o.get("restaurante_id")}, {"nombre": 1})

        o["_id"] = str(o["_id"])
        o["usuario_id"] = str(o["usuario_id"])
        o["restaurante_id"] = str(o["restaurante_id"])
        o["usuario_nombre"] = (
            f"{usuario.get('nombre', '')} {usuario.get('apellido', '')}".strip()
            if usuario
            else "Usuario"
        )
        o["restaurante_nombre"] = restaurante.get("nombre") if restaurante else "Restaurante"
        if "total" in o:
            o["total"] = str(o["total"])

    return ordenes


@router.get("/{order_id}")
def get_order_detail(order_id: str):
    try:
        oid = ObjectId(order_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID de orden inválido")

    orden = db.ordenes.find_one({"_id": oid})
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    orden["_id"] = str(orden["_id"])
    orden["usuario_id"] = str(orden["usuario_id"])
    orden["restaurante_id"] = str(orden["restaurante_id"])

    usuario = db.usuarios.find_one({"_id": ObjectId(orden["usuario_id"])}, {"nombre": 1, "apellido": 1})
    restaurante = db.restaurantes.find_one({"_id": ObjectId(orden["restaurante_id"])}, {"nombre": 1})
    orden["usuario_nombre"] = (
        f"{usuario.get('nombre', '')} {usuario.get('apellido', '')}".strip()
        if usuario
        else "Usuario"
    )
    orden["restaurante_nombre"] = restaurante.get("nombre") if restaurante else "Restaurante"

    if "total" in orden:
        orden["total"] = str(orden["total"])
    if "subtotal" in orden:
        orden["subtotal"] = str(orden["subtotal"])
    if "impuesto" in orden:
        orden["impuesto"] = str(orden["impuesto"])

    for item in orden.get("items", []):
        if "articulo_id" in item:
            item["articulo_id"] = str(item["articulo_id"])
        if "precio_unitario" in item:
            item["precio_unitario"] = str(item["precio_unitario"])
        if "subtotal" in item:
            item["subtotal"] = str(item["subtotal"])

    return orden


@router.post("/")
def create_order(payload: OrderCreate):
    try:
        resultado = crear_orden_y_actualizar_puntos(
            usuario_id=ObjectId(payload.usuario_id),
            restaurante_id=ObjectId(payload.restaurante_id),
            metodo_pago=payload.metodo_pago,
            items=[
                {
                    "articulo_id": ObjectId(item.articulo_id),
                    "cantidad": item.cantidad,
                }
                for item in payload.items
            ],
        )
        resultado["orden_id"] = str(resultado["orden_id"])
        return resultado
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{order_id}/status")
def update_order_status(order_id: str, payload: UpdateStatusRequest):
    try:
        count = cambiar_estado_orden(ObjectId(order_id), payload.nuevo_estado, db=db)
        if count == 0:
            raise HTTPException(status_code=404, detail="Orden no encontrada o transición inválida")
        return {"message": f"Estado actualizado a '{payload.nuevo_estado}'", "modified": count}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{order_id}")
def delete_order(order_id: str):
    try:
        oid = ObjectId(order_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID de orden inválido")

    result = db.ordenes.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return {"message": "Orden eliminada", "deleted": result.deleted_count}