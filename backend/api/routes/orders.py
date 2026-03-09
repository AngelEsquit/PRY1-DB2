from fastapi import APIRouter, HTTPException
from bson import ObjectId

from crud.common import db
from transactions.transactions import crear_orden_y_actualizar_puntos
from api.schemas import OrderCreate

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("/")
def get_orders():
    ordenes = list(
        db.ordenes.find(
            {},
            {
                "usuario_id": 1,
                "restaurante_id": 1,
                "estado": 1,
                "fecha_pedido": 1,
                "total": 1,
            },
        ).sort("fecha_pedido", -1).limit(50)
    )

    for o in ordenes:
        o["_id"] = str(o["_id"])
        o["usuario_id"] = str(o["usuario_id"])
        o["restaurante_id"] = str(o["restaurante_id"])
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