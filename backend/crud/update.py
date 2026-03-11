from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pymongo import UpdateOne
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError

from .common import (
    ORDER_STATE_TRANSITIONS,
    VALID_ORDER_STATES,
    quantize_money,
    resolve_db,
    to_decimal,
    to_decimal128,
    to_object_id,
)


def actualizar_telefono_restaurante(
    restaurante_id: Any,
    nuevo_telefono: str,
    db: Optional[Database] = None,
) -> int:
    db = resolve_db(db)
    rest_oid = to_object_id(restaurante_id, "restaurante_id")
    result = db.restaurantes.update_one({"_id": rest_oid}, {"$set": {"telefono": nuevo_telefono}})
    return result.modified_count


def actualizar_email_usuario(usuario_id: Any, nuevo_email: str, db: Optional[Database] = None) -> int:
    db = resolve_db(db)
    user_oid = to_object_id(usuario_id, "usuario_id")

    try:
        result = db.usuarios.update_one({"_id": user_oid}, {"$set": {"email": nuevo_email}})
    except DuplicateKeyError as exc:
        raise ValueError("El nuevo email ya existe") from exc

    return result.modified_count


def cambiar_estado_orden(orden_id: Any, nuevo_estado: str, db: Optional[Database] = None) -> int:
    db = resolve_db(db)
    order_oid = to_object_id(orden_id, "orden_id")

    if nuevo_estado not in VALID_ORDER_STATES:
        raise ValueError("Estado no permitido")

    orden = db.ordenes.find_one({"_id": order_oid}, {"estado": 1})
    if not orden:
        raise ValueError("Orden no encontrada")

    estado_actual = orden.get("estado")
    allowed = ORDER_STATE_TRANSITIONS.get(estado_actual, set())
    if nuevo_estado not in allowed:
        raise ValueError(f"Transicion invalida: {estado_actual} -> {nuevo_estado}")

    result = db.ordenes.update_one({"_id": order_oid}, {"$set": {"estado": nuevo_estado}})
    return result.modified_count


def actualizar_precio_articulo(articulo_id: Any, nuevo_precio: Any, db: Optional[Database] = None) -> int:
    db = resolve_db(db)
    art_oid = to_object_id(articulo_id, "articulo_id")

    result = db.articulos_menu.update_one(
        {"_id": art_oid},
        {"$set": {"precio": to_decimal128(nuevo_precio)}},
    )
    return result.modified_count


def desactivar_usuarios_inactivos(meses_inactividad: int = 6, db: Optional[Database] = None) -> int:
    db = resolve_db(db)
    cutoff = datetime.utcnow() - timedelta(days=30 * int(meses_inactividad))

    activos = db.ordenes.distinct("usuario_id", {"fecha_pedido": {"$gte": cutoff}})
    result = db.usuarios.update_many({"_id": {"$nin": activos}}, {"$set": {"activo": False}})
    return result.modified_count


def aplicar_descuento_por_categoria(
    categoria: str,
    porcentaje_descuento: float,
    db: Optional[Database] = None,
) -> Dict[str, int]:
    db = resolve_db(db)

    if porcentaje_descuento <= 0 or porcentaje_descuento >= 100:
        raise ValueError("porcentaje_descuento debe estar entre 0 y 100")

    factor = Decimal("1") - (Decimal(str(porcentaje_descuento)) / Decimal("100"))

    cursor = db.articulos_menu.find({"categoria": categoria}, {"_id": 1, "precio": 1})
    ops: List[UpdateOne] = []

    for articulo in cursor:
        precio_actual = to_decimal(articulo["precio"])
        precio_nuevo = quantize_money(precio_actual * factor)
        ops.append(
            UpdateOne(
                {"_id": articulo["_id"]},
                {"$set": {"precio": to_decimal128(precio_nuevo)}},
            )
        )

    if not ops:
        return {"matched": 0, "modified": 0}

    result = db.articulos_menu.bulk_write(ops, ordered=False)
    return {"matched": result.matched_count, "modified": result.modified_count}


def marcar_ordenes_anticuadas(db: Optional[Database] = None) -> int:
    db = resolve_db(db)
    cutoff = datetime.utcnow() - timedelta(days=365)
    result = db.ordenes.update_many(
        {
            "fecha_pedido": {"$lt": cutoff},
            "estado": {"$nin": ["archivada"]},
        },
        {"$set": {"estado": "archivada"}},
    )
    return result.modified_count


def actualizar_direccion_restaurante(
    restaurante_id: Any,
    calle: str,
    ciudad: str,
    codigo_postal: str,
    db: Optional[Database] = None,
) -> int:
    """
    Actualiza la dirección embebida de un restaurante.
    """
    db = resolve_db(db)
    rest_oid = to_object_id(restaurante_id, "restaurante_id")
    
    nueva_direccion = {
        "calle": calle,
        "ciudad": ciudad,
        "codigo_postal": codigo_postal,
    }
    
    result = db.restaurantes.update_one(
        {"_id": rest_oid},
        {"$set": {"direccion": nueva_direccion}}
    )
    return result.modified_count
