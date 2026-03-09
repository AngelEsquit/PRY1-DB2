from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from bson import ObjectId
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError

from .common import (
    quantize_money,
    resolve_db,
    to_decimal,
    to_decimal128,
    to_object_id,
)


def crear_restaurante(datos_restaurante: Dict[str, Any], db: Optional[Database] = None) -> ObjectId:
    db = resolve_db(db)

    required = [
        "nombre",
        "descripcion",
        "tipo_comida",
        "direccion",
        "ubicacion",
        "horario",
        "telefono",
        "email",
    ]
    for key in required:
        if key not in datos_restaurante:
            raise ValueError(f"Falta campo obligatorio: {key}")

    direccion = dict(datos_restaurante["direccion"])
    direccion["pais"] = "Guatemala"

    restaurante = {
        "nombre": datos_restaurante["nombre"],
        "descripcion": datos_restaurante["descripcion"],
        "tipo_comida": list(datos_restaurante.get("tipo_comida", [])),
        "direccion": direccion,
        "ubicacion": datos_restaurante["ubicacion"],
        "horario": datos_restaurante["horario"],
        "telefono": datos_restaurante["telefono"],
        "email": datos_restaurante["email"],
        "fecha_registro": datetime.utcnow(),
        "activo": True,
    }

    result = db.restaurantes.insert_one(restaurante)
    return result.inserted_id


def crear_usuario(
    nombre: str,
    apellido: str,
    email: str,
    telefono: str,
    direccion: Dict[str, Any],
    db: Optional[Database] = None,
) -> ObjectId:
    db = resolve_db(db)

    if db.usuarios.find_one({"email": email}, {"_id": 1}):
        raise ValueError("El email ya existe")

    direccion_payload = dict(direccion)
    direccion_payload["pais"] = "Guatemala"

    usuario = {
        "nombre": nombre,
        "apellido": apellido,
        "email": email,
        "telefono": telefono,
        "direccion": direccion_payload,
        "fecha_registro": datetime.utcnow(),
        "tipo": "regular",
        "preferencias": [],
        "puntos": 0,
        "activo": True,
    }

    try:
        result = db.usuarios.insert_one(usuario)
    except DuplicateKeyError as exc:
        raise ValueError("El email ya existe") from exc

    return result.inserted_id


def crear_articulo_menu(
    restaurante_id: Any,
    datos_articulo: Dict[str, Any],
    db: Optional[Database] = None,
) -> ObjectId:
    db = resolve_db(db)
    rest_oid = to_object_id(restaurante_id, "restaurante_id")

    if not db.restaurantes.find_one({"_id": rest_oid}, {"_id": 1}):
        raise ValueError("El restaurante_id no existe")

    required = [
        "nombre",
        "descripcion",
        "categoria",
        "precio",
        "ingredientes",
        "opciones_personalizacion",
        "tiempo_preparacion",
    ]
    for key in required:
        if key not in datos_articulo:
            raise ValueError(f"Falta campo obligatorio en articulo: {key}")

    articulo = {
        "restaurante_id": rest_oid,
        "nombre": datos_articulo["nombre"],
        "descripcion": datos_articulo["descripcion"],
        "categoria": datos_articulo["categoria"],
        "precio": to_decimal128(datos_articulo["precio"]),
        "moneda": "GTQ",
        "disponible": bool(datos_articulo.get("disponible", True)),
        "ingredientes": list(datos_articulo.get("ingredientes", [])),
        "opciones_personalizacion": list(datos_articulo.get("opciones_personalizacion", [])),
        "calorias": datos_articulo.get("calorias"),
        "tiempo_preparacion": int(datos_articulo["tiempo_preparacion"]),
    }

    result = db.articulos_menu.insert_one(articulo)
    return result.inserted_id


def crear_orden(
    usuario_id: Any,
    restaurante_id: Any,
    items_seleccionados: List[Dict[str, Any]],
    metodo_pago: str,
    direccion_entrega: Optional[Dict[str, Any]] = None,
    db: Optional[Database] = None,
) -> Dict[str, Any]:
    db = resolve_db(db)
    user_oid = to_object_id(usuario_id, "usuario_id")
    rest_oid = to_object_id(restaurante_id, "restaurante_id")

    usuario = db.usuarios.find_one({"_id": user_oid})
    if not usuario:
        raise ValueError("El usuario_id no existe")

    if not db.restaurantes.find_one({"_id": rest_oid}, {"_id": 1}):
        raise ValueError("El restaurante_id no existe")

    if not items_seleccionados:
        raise ValueError("La orden debe contener al menos un item")

    items = []
    subtotal_total = Decimal("0")

    for item in items_seleccionados:
        articulo_oid = to_object_id(item.get("articulo_id"), "articulo_id")
        cantidad = int(item.get("cantidad", 0))
        personalizaciones = list(item.get("personalizaciones", []))

        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")

        articulo = db.articulos_menu.find_one(
            {"_id": articulo_oid, "restaurante_id": rest_oid},
            {"_id": 1, "nombre": 1, "precio": 1},
        )
        if not articulo:
            raise ValueError(f"Articulo {articulo_oid} no existe en el restaurante indicado")

        precio_unitario = to_decimal(articulo["precio"])
        subtotal_item = quantize_money(precio_unitario * Decimal(cantidad))
        subtotal_total += subtotal_item

        items.append(
            {
                "articulo_id": articulo_oid,
                "nombre": articulo["nombre"],
                "cantidad": cantidad,
                "precio_unitario": to_decimal128(precio_unitario),
                "subtotal": to_decimal128(subtotal_item),
                "personalizaciones": personalizaciones,
            }
        )

    subtotal_total = quantize_money(subtotal_total)
    impuesto = quantize_money(subtotal_total * Decimal("0.12"))
    total = quantize_money(subtotal_total + impuesto)

    direccion_final = direccion_entrega if direccion_entrega is not None else usuario.get("direccion")

    orden = {
        "usuario_id": user_oid,
        "restaurante_id": rest_oid,
        "fecha_pedido": datetime.utcnow(),
        "items": items,
        "subtotal": to_decimal128(subtotal_total),
        "impuesto": to_decimal128(impuesto),
        "total": to_decimal128(total),
        "estado": "pendiente",
        "metodo_pago": metodo_pago,
        "direccion_entrega": direccion_final,
        "calificacion_entrega": None,
    }

    result = db.ordenes.insert_one(orden)
    orden["_id"] = result.inserted_id
    return orden


def crear_resena(
    usuario_id: Any,
    restaurante_id: Any,
    calificacion: int,
    titulo: str,
    comentario: str,
    orden_id: Optional[Any] = None,
    fotos: Optional[List[str]] = None,
    db: Optional[Database] = None,
) -> ObjectId:
    db = resolve_db(db)
    user_oid = to_object_id(usuario_id, "usuario_id")
    rest_oid = to_object_id(restaurante_id, "restaurante_id")

    if not (1 <= int(calificacion) <= 5):
        raise ValueError("calificacion debe estar entre 1 y 5")

    if not db.usuarios.find_one({"_id": user_oid}, {"_id": 1}):
        raise ValueError("El usuario_id no existe")

    if not db.restaurantes.find_one({"_id": rest_oid}, {"_id": 1}):
        raise ValueError("El restaurante_id no existe")

    order_oid = None
    if orden_id is not None:
        order_oid = to_object_id(orden_id, "orden_id")
        orden = db.ordenes.find_one({"_id": order_oid}, {"_id": 1, "usuario_id": 1})
        if not orden:
            raise ValueError("La orden no existe")
        if orden.get("usuario_id") != user_oid:
            raise ValueError("La orden no pertenece al usuario indicado")

    resena = {
        "usuario_id": user_oid,
        "restaurante_id": rest_oid,
        "orden_id": order_oid,
        "fecha": datetime.utcnow(),
        "calificacion_general": int(calificacion),
        "titulo": titulo,
        "comentario": comentario,
        "fotos": list(fotos or []),
        "likes": 0,
        "respuesta_restaurante": None,
        "items_resenados": [],
    }

    result = db.resenas.insert_one(resena)
    return result.inserted_id
