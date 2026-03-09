from datetime import datetime
from decimal import Decimal
from pymongo import ReturnDocument

from crud.common import client, db, quantize_money, to_decimal, to_decimal128


def crear_orden_y_actualizar_puntos(
    usuario_id,
    restaurante_id,
    items,
    metodo_pago="efectivo",
):
    """
    Crea una orden y actualiza los puntos del usuario dentro de una transacción.

    items:
    [
        {"articulo_id": ObjectId(...), "cantidad": 2},
        ...
    ]
    """

    with client.start_session() as session:
        with session.start_transaction():
            articulos_detalle = []
            subtotal_total = Decimal("0")

            for item in items:
                articulo = db.articulos_menu.find_one(
                    {
                        "_id": item["articulo_id"],
                        "restaurante_id": restaurante_id,
                        "disponible": True,
                    },
                    session=session,
                )

                if not articulo:
                    raise ValueError(
                        f"No se encontró o no está disponible el artículo {item['articulo_id']}"
                    )

                cantidad = int(item["cantidad"])
                if cantidad <= 0:
                    raise ValueError("La cantidad debe ser mayor a 0")

                precio_unitario = to_decimal(articulo["precio"])
                subtotal_item = quantize_money(precio_unitario * Decimal(cantidad))
                subtotal_total += subtotal_item

                articulos_detalle.append(
                    {
                        "articulo_id": articulo["_id"],
                        "nombre": articulo["nombre"],
                        "precio_unitario": to_decimal128(precio_unitario),
                        "cantidad": cantidad,
                        "subtotal": to_decimal128(subtotal_item),
                    }
                )

            subtotal_total = quantize_money(subtotal_total)
            impuesto = quantize_money(subtotal_total * Decimal("0.12"))
            total = quantize_money(subtotal_total + impuesto)
            puntos_ganados = int(total // Decimal("10"))

            nueva_orden = {
                "usuario_id": usuario_id,
                "restaurante_id": restaurante_id,
                "items": articulos_detalle,
                "metodo_pago": metodo_pago,
                "estado": "pendiente",
                "fecha_pedido": datetime.utcnow(),
                "subtotal": to_decimal128(subtotal_total),
                "impuesto": to_decimal128(impuesto),
                "total": to_decimal128(total),
                "calificacion_entrega": None,
            }

            resultado_orden = db.ordenes.insert_one(nueva_orden, session=session)

            usuario_actualizado = db.usuarios.find_one_and_update(
                {"_id": usuario_id},
                {"$inc": {"puntos": puntos_ganados}},
                return_document=ReturnDocument.AFTER,
                session=session,
            )

            return {
                "ok": True,
                "orden_id": resultado_orden.inserted_id,
                "subtotal": str(subtotal_total),
                "impuesto": str(impuesto),
                "total": str(total),
                "puntos_ganados": puntos_ganados,
                "puntos_usuario_actuales": usuario_actualizado["puntos"]
                if usuario_actualizado
                else None,
            }


def eliminar_usuario_con_dependencias(usuario_id):
    """
    Elimina un usuario junto con todas sus órdenes y reseñas asociadas en una transacción.
    """

    with client.start_session() as session:
        with session.start_transaction():
            usuario = db.usuarios.find_one({"_id": usuario_id}, session=session)

            if not usuario:
                raise ValueError("Usuario no encontrado")

            delete_ordenes = db.ordenes.delete_many(
                {"usuario_id": usuario_id},
                session=session,
            )

            delete_resenas = db.resenas.delete_many(
                {"usuario_id": usuario_id},
                session=session,
            )

            delete_usuario = db.usuarios.delete_one(
                {"_id": usuario_id},
                session=session,
            )

            return {
                "ok": True,
                "usuario_eliminado": delete_usuario.deleted_count,
                "ordenes_eliminadas": delete_ordenes.deleted_count,
                "resenas_eliminadas": delete_resenas.deleted_count,
            }