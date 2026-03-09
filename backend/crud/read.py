from datetime import datetime
from typing import Any, Dict, List, Optional

from pymongo import ASCENDING, DESCENDING
from pymongo.database import Database

from .common import VALID_USER_TYPES, resolve_db, to_object_id


def buscar_restaurantes_por_tipo(tipo_comida: str, db: Optional[Database] = None) -> List[Dict[str, Any]]:
    db = resolve_db(db)
    return list(db.restaurantes.find({"tipo_comida": tipo_comida}))


def buscar_restaurantes_por_nombre(nombre: str, db: Optional[Database] = None) -> List[Dict[str, Any]]:
    db = resolve_db(db)
    return list(db.restaurantes.find({"nombre": {"$regex": nombre, "$options": "i"}}))


def buscar_usuarios_por_tipo(tipo: str, db: Optional[Database] = None) -> List[Dict[str, Any]]:
    db = resolve_db(db)
    if tipo not in VALID_USER_TYPES:
        raise ValueError("tipo debe ser regular, premium o vip")
    return list(db.usuarios.find({"tipo": tipo}))


def buscar_ordenes_por_estado(estado: str, db: Optional[Database] = None) -> List[Dict[str, Any]]:
    db = resolve_db(db)
    return list(db.ordenes.find({"estado": estado}))


def buscar_ordenes_por_rango_fechas(
    fecha_inicio: datetime,
    fecha_fin: datetime,
    db: Optional[Database] = None,
) -> List[Dict[str, Any]]:
    db = resolve_db(db)
    return list(db.ordenes.find({"fecha_pedido": {"$gte": fecha_inicio, "$lte": fecha_fin}}))


def buscar_resenas_por_calificacion(
    min_calif: int,
    max_calif: int,
    db: Optional[Database] = None,
) -> List[Dict[str, Any]]:
    db = resolve_db(db)
    return list(
        db.resenas.find({"calificacion_general": {"$gte": int(min_calif), "$lte": int(max_calif)}})
    )


def obtener_nombres_restaurantes(db: Optional[Database] = None) -> List[Dict[str, Any]]:
    db = resolve_db(db)
    projection = {"_id": 1, "nombre": 1, "telefono": 1}
    return list(db.restaurantes.find({}, projection))


def obtener_datos_basicos_usuario(usuario_id: Any, db: Optional[Database] = None) -> Optional[Dict[str, Any]]:
    db = resolve_db(db)
    user_oid = to_object_id(usuario_id, "usuario_id")
    projection = {"_id": 0, "nombre": 1, "email": 1, "tipo": 1, "puntos": 1}
    return db.usuarios.find_one({"_id": user_oid}, projection)


def obtener_resumen_orden(orden_id: Any, db: Optional[Database] = None) -> Optional[Dict[str, Any]]:
    db = resolve_db(db)
    order_oid = to_object_id(orden_id, "orden_id")
    projection = {"_id": 0, "fecha_pedido": 1, "total": 1, "estado": 1}
    return db.ordenes.find_one({"_id": order_oid}, projection)


def ordenes_mas_recientes(limite: int = 10, db: Optional[Database] = None) -> List[Dict[str, Any]]:
    db = resolve_db(db)
    return list(db.ordenes.find().sort("fecha_pedido", DESCENDING).limit(int(limite)))


def restaurantes_por_nombre_ascendente(db: Optional[Database] = None) -> List[Dict[str, Any]]:
    db = resolve_db(db)
    return list(db.restaurantes.find().sort("nombre", ASCENDING))


def mejores_calificaciones(limite: int = 10, db: Optional[Database] = None) -> List[Dict[str, Any]]:
    db = resolve_db(db)
    return list(db.resenas.find().sort("calificacion_general", DESCENDING).limit(int(limite)))


def listar_restaurantes_paginados(
    pagina: int = 1,
    por_pagina: int = 10,
    db: Optional[Database] = None,
) -> List[Dict[str, Any]]:
    db = resolve_db(db)
    page = max(1, int(pagina))
    size = max(1, int(por_pagina))
    skip = (page - 1) * size
    return list(db.restaurantes.find().skip(skip).limit(size))


def listar_ordenes_usuario(
    usuario_id: Any,
    pagina: int = 1,
    por_pagina: int = 20,
    db: Optional[Database] = None,
) -> List[Dict[str, Any]]:
    db = resolve_db(db)
    user_oid = to_object_id(usuario_id, "usuario_id")
    page = max(1, int(pagina))
    size = max(1, int(por_pagina))
    skip = (page - 1) * size
    return list(
        db.ordenes.find({"usuario_id": user_oid})
        .sort("fecha_pedido", DESCENDING)
        .skip(skip)
        .limit(size)
    )


def ordenes_con_detalles_completos(orden_id: Any, db: Optional[Database] = None) -> Optional[Dict[str, Any]]:
    db = resolve_db(db)
    order_oid = to_object_id(orden_id, "orden_id")

    pipeline = [
        {"$match": {"_id": order_oid}},
        {
            "$lookup": {
                "from": "usuarios",
                "localField": "usuario_id",
                "foreignField": "_id",
                "as": "usuario",
            }
        },
        {
            "$lookup": {
                "from": "restaurantes",
                "localField": "restaurante_id",
                "foreignField": "_id",
                "as": "restaurante",
            }
        },
        {
            "$project": {
                "_id": 1,
                "fecha_pedido": 1,
                "estado": 1,
                "total": 1,
                "items": 1,
                "usuario": {"$arrayElemAt": ["$usuario", 0]},
                "restaurante": {"$arrayElemAt": ["$restaurante", 0]},
            }
        },
    ]

    result = list(db.ordenes.aggregate(pipeline))
    return result[0] if result else None


def articulos_con_restaurante(articulo_id: Any, db: Optional[Database] = None) -> Optional[Dict[str, Any]]:
    db = resolve_db(db)
    art_oid = to_object_id(articulo_id, "articulo_id")

    pipeline = [
        {"$match": {"_id": art_oid}},
        {
            "$lookup": {
                "from": "restaurantes",
                "localField": "restaurante_id",
                "foreignField": "_id",
                "as": "restaurante",
            }
        },
        {
            "$project": {
                "_id": 1,
                "nombre": 1,
                "categoria": 1,
                "precio": 1,
                "restaurante": {"$arrayElemAt": ["$restaurante", 0]},
            }
        },
    ]

    result = list(db.articulos_menu.aggregate(pipeline))
    return result[0] if result else None


def resenas_con_usuario_y_restaurante(resena_id: Any, db: Optional[Database] = None) -> Optional[Dict[str, Any]]:
    db = resolve_db(db)
    rev_oid = to_object_id(resena_id, "resena_id")

    pipeline = [
        {"$match": {"_id": rev_oid}},
        {
            "$lookup": {
                "from": "usuarios",
                "localField": "usuario_id",
                "foreignField": "_id",
                "as": "usuario",
            }
        },
        {
            "$lookup": {
                "from": "restaurantes",
                "localField": "restaurante_id",
                "foreignField": "_id",
                "as": "restaurante",
            }
        },
        {
            "$project": {
                "_id": 1,
                "fecha": 1,
                "calificacion_general": 1,
                "titulo": 1,
                "comentario": 1,
                "usuario": {"$arrayElemAt": ["$usuario", 0]},
                "restaurante": {"$arrayElemAt": ["$restaurante", 0]},
            }
        },
    ]

    result = list(db.resenas.aggregate(pipeline))
    return result[0] if result else None


def historial_completo_usuario(usuario_id: Any, db: Optional[Database] = None) -> Dict[str, Any]:
    db = resolve_db(db)
    user_oid = to_object_id(usuario_id, "usuario_id")

    usuario = db.usuarios.find_one({"_id": user_oid})
    if not usuario:
        raise ValueError("Usuario no encontrado")

    ordenes = list(db.ordenes.find({"usuario_id": user_oid}).sort("fecha_pedido", DESCENDING))
    resenas = list(db.resenas.find({"usuario_id": user_oid}).sort("fecha", DESCENDING))

    return {
        "usuario": usuario,
        "ordenes": ordenes,
        "resenas": resenas,
    }
