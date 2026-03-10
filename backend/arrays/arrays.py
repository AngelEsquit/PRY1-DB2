from crud.common import db


def agregar_preferencia_usuario(usuario_id, nueva_preferencia):
    """
    Agrega una preferencia al array preferencias usando $addToSet
    para evitar duplicados.
    """
    resultado = db.usuarios.update_one(
        {"_id": usuario_id},
        {
            "$addToSet": {
                "preferencias": nueva_preferencia
            }
        }
    )

    return {
        "matched": resultado.matched_count,
        "modified": resultado.modified_count
    }


def eliminar_preferencia_usuario(usuario_id, preferencia):
    """
    Elimina una preferencia del array preferencias usando $pull.
    """
    resultado = db.usuarios.update_one(
        {"_id": usuario_id},
        {
            "$pull": {
                "preferencias": preferencia
            }
        }
    )

    return {
        "matched": resultado.matched_count,
        "modified": resultado.modified_count
    }


def agregar_horario_restaurante(restaurante_id, nuevo_horario):
    """
    Agrega un horario al array horario usando $push.
    Primero convierte el campo a array si es necesario (migración).
    """
    # Migración: si horario es un objeto, conviértelo a array
    db.restaurantes.update_one(
        {"_id": restaurante_id, "horario": {"$type": "object"}},
        {"$set": {"horario": []}}
    )
    
    resultado = db.restaurantes.update_one(
        {"_id": restaurante_id},
        {
            "$push": {
                "horario": nuevo_horario
            }
        }
    )

    return {
        "matched": resultado.matched_count,
        "modified": resultado.modified_count
    }


def agregar_respuesta_resena(resena_id, respuesta):
    """
    Agrega una respuesta dentro de un array de respuestas en la reseña.
    """
    resultado = db.resenas.update_one(
        {"_id": resena_id},
        {
            "$push": {
                "respuestas": respuesta
            }
        }
    )

    return {
        "matched": resultado.matched_count,
        "modified": resultado.modified_count
    }


def eliminar_respuesta_resena(resena_id, texto_respuesta):
    """
    Elimina una respuesta de una reseña usando $pull.
    """
    resultado = db.resenas.update_one(
        {"_id": resena_id},
        {
            "$pull": {
                "respuestas": {
                    "texto": texto_respuesta
                }
            }
        }
    )

    return {
        "matched": resultado.matched_count,
        "modified": resultado.modified_count
    }