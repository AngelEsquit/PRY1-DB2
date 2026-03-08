from datetime import datetime, timedelta
from typing import Any, Optional

from pymongo.database import Database

from .common import resolve_db, to_object_id


def eliminar_resena(resena_id: Any, db: Optional[Database] = None) -> int:
    db = resolve_db(db)
    rev_oid = to_object_id(resena_id, "resena_id")
    result = db.resenas.delete_one({"_id": rev_oid})
    return result.deleted_count


def eliminar_articulo_menu(articulo_id: Any, db: Optional[Database] = None) -> int:
    db = resolve_db(db)
    art_oid = to_object_id(articulo_id, "articulo_id")

    dependencia = db.ordenes.find_one(
        {
            "estado": {"$nin": ["cancelado", "archivada"]},
            "items.articulo_id": art_oid,
        },
        {"_id": 1},
    )
    if dependencia:
        raise ValueError("No se puede eliminar: articulo presente en ordenes activas")

    result = db.articulos_menu.delete_one({"_id": art_oid})
    return result.deleted_count


def eliminar_usuario(usuario_id: Any, db: Optional[Database] = None) -> int:
    db = resolve_db(db)
    user_oid = to_object_id(usuario_id, "usuario_id")

    has_orders = db.ordenes.find_one({"usuario_id": user_oid}, {"_id": 1})
    has_reviews = db.resenas.find_one({"usuario_id": user_oid}, {"_id": 1})
    if has_orders or has_reviews:
        raise ValueError("No se puede eliminar usuario con dependencias en ordenes o resenas")

    result = db.usuarios.delete_one({"_id": user_oid})
    return result.deleted_count


def limpiar_resenas_antiguas(años: int = 2, db: Optional[Database] = None) -> int:
    db = resolve_db(db)
    cutoff = datetime.utcnow() - timedelta(days=365 * int(años))
    result = db.resenas.delete_many({"fecha": {"$lt": cutoff}})
    return result.deleted_count


def eliminar_usuarios_inactivos(db: Optional[Database] = None) -> int:
    db = resolve_db(db)

    candidatos = db.usuarios.find({"activo": False}, {"_id": 1})
    ids = [doc["_id"] for doc in candidatos]
    if not ids:
        return 0

    users_with_orders = set(db.ordenes.distinct("usuario_id", {"usuario_id": {"$in": ids}}))
    removable = [uid for uid in ids if uid not in users_with_orders]

    if not removable:
        return 0

    result = db.usuarios.delete_many({"_id": {"$in": removable}})
    return result.deleted_count


def limpiar_ordenes_canceladas(db: Optional[Database] = None) -> int:
    db = resolve_db(db)
    cutoff = datetime.utcnow() - timedelta(days=30)
    result = db.ordenes.delete_many({"estado": "cancelado", "fecha_pedido": {"$lt": cutoff}})
    return result.deleted_count
