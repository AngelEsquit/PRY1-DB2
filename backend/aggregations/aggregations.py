from datetime import datetime
from bson import ObjectId
from crud.common import db


def platillos_mas_vendidos_mes(anio, mes, restaurante_id=None, limite=10):
    """
    Obtiene los platillos más vendidos del mes.

    Si se manda restaurante_id:
        devuelve los platillos más vendidos de ESE restaurante en ese mes.

    Si no se manda restaurante_id:
        devuelve los platillos más vendidos por restaurante en ese mes.
    """

    fecha_inicio = datetime(anio, mes, 1)

    if mes == 12:
        fecha_fin = datetime(anio + 1, 1, 1)
    else:
        fecha_fin = datetime(anio, mes + 1, 1)

    match_stage = {
        "fecha_pedido": {
            "$gte": fecha_inicio,
            "$lt": fecha_fin
        }
    }

    if restaurante_id:
        if isinstance(restaurante_id, str):
            restaurante_id = ObjectId(restaurante_id)
        match_stage["restaurante_id"] = restaurante_id

    pipeline = [
        {
            "$match": match_stage
        },
        {
            "$unwind": "$items"
        },
        {
            "$group": {
                "_id": {
                    "restaurante_id": "$restaurante_id",
                    "articulo_id": "$items.articulo_id"
                },
                "nombre_platillo": {"$first": "$items.nombre"},
                "cantidad_vendida": {"$sum": "$items.cantidad"},
                "ingresos_generados": {"$sum": {"$toDouble": "$items.subtotal"}}
            }
        },
        {
            "$lookup": {
                "from": "restaurantes",
                "localField": "_id.restaurante_id",
                "foreignField": "_id",
                "as": "restaurante"
            }
        },
        {
            "$unwind": "$restaurante"
        },
        {
            "$project": {
                "_id": 0,
                "restaurante_id": "$_id.restaurante_id",
                "articulo_id": "$_id.articulo_id",
                "restaurante": "$restaurante.nombre",
                "platillo": "$nombre_platillo",
                "cantidad_vendida": 1,
                "ingresos_generados": {"$round": ["$ingresos_generados", 2]}
            }
        },
        {
            "$sort": {
                "cantidad_vendida": -1,
                "ingresos_generados": -1
            }
        },
        {
            "$limit": limite
        }
    ]

    return list(db.ordenes.aggregate(pipeline))


def platillo_top_por_restaurante_en_mes(anio, mes):
    """
    Devuelve SOLO el platillo top de cada restaurante en el mes indicado.
    Esto se alinea mejor con 'cuál es el platillo más vendido por restaurante en el mes'.
    """

    fecha_inicio = datetime(anio, mes, 1)

    if mes == 12:
        fecha_fin = datetime(anio + 1, 1, 1)
    else:
        fecha_fin = datetime(anio, mes + 1, 1)

    pipeline = [
        {
            "$match": {
                "fecha_pedido": {
                    "$gte": fecha_inicio,
                    "$lt": fecha_fin
                }
            }
        },
        {
            "$unwind": "$items"
        },
        {
            "$group": {
                "_id": {
                    "restaurante_id": "$restaurante_id",
                    "articulo_id": "$items.articulo_id"
                },
                "nombre_platillo": {"$first": "$items.nombre"},
                "cantidad_vendida": {"$sum": "$items.cantidad"},
                "ingresos_generados": {"$sum": {"$toDouble": "$items.subtotal"}}
            }
        },
        {
            "$sort": {
                "_id.restaurante_id": 1,
                "cantidad_vendida": -1,
                "ingresos_generados": -1
            }
        },
        {
            "$group": {
                "_id": "$_id.restaurante_id",
                "platillo_top": {"$first": "$nombre_platillo"},
                "cantidad_vendida": {"$first": "$cantidad_vendida"},
                "ingresos_generados": {"$first": "$ingresos_generados"},
                "articulo_id": {"$first": "$_id.articulo_id"}
            }
        },
        {
            "$lookup": {
                "from": "restaurantes",
                "localField": "_id",
                "foreignField": "_id",
                "as": "restaurante"
            }
        },
        {
            "$unwind": "$restaurante"
        },
        {
            "$project": {
                "_id": 0,
                "restaurante_id": "$_id",
                "restaurante": "$restaurante.nombre",
                "articulo_id": 1,
                "platillo_top": 1,
                "cantidad_vendida": 1,
                "ingresos_generados": {"$round": ["$ingresos_generados", 2]}
            }
        },
        {
            "$sort": {
                "cantidad_vendida": -1
            }
        }
    ]

    return list(db.ordenes.aggregate(pipeline))


def restaurantes_mejor_calificados(min_resenas=5, limite=10):
    pipeline = [
        {
            "$group": {
                "_id": "$restaurante_id",
                "promedio_calificacion": {"$avg": "$calificacion_general"},
                "total_resenas": {"$sum": 1},
                "calif_1": {
                    "$sum": {
                        "$cond": [{"$eq": ["$calificacion_general", 1]}, 1, 0]
                    }
                },
                "calif_2": {
                    "$sum": {
                        "$cond": [{"$eq": ["$calificacion_general", 2]}, 1, 0]
                    }
                },
                "calif_3": {
                    "$sum": {
                        "$cond": [{"$eq": ["$calificacion_general", 3]}, 1, 0]
                    }
                },
                "calif_4": {
                    "$sum": {
                        "$cond": [{"$eq": ["$calificacion_general", 4]}, 1, 0]
                    }
                },
                "calif_5": {
                    "$sum": {
                        "$cond": [{"$eq": ["$calificacion_general", 5]}, 1, 0]
                    }
                }
            }
        },
        {
            "$match": {
                "total_resenas": {"$gte": min_resenas}
            }
        },
        {
            "$lookup": {
                "from": "restaurantes",
                "localField": "_id",
                "foreignField": "_id",
                "as": "restaurante"
            }
        },
        {
            "$unwind": "$restaurante"
        },
        {
            "$project": {
                "_id": 0,
                "restaurante_id": "$restaurante._id",
                "nombre": "$restaurante.nombre",
                "tipo_comida": "$restaurante.tipo_comida",
                "promedio_calificacion": {"$round": ["$promedio_calificacion", 2]},
                "total_resenas": 1,
                "distribucion_calificaciones": {
                    "1_estrella": "$calif_1",
                    "2_estrellas": "$calif_2",
                    "3_estrellas": "$calif_3",
                    "4_estrellas": "$calif_4",
                    "5_estrellas": "$calif_5"
                }
            }
        },
        {
            "$sort": {
                "promedio_calificacion": -1,
                "total_resenas": -1
            }
        },
        {
            "$limit": limite
        }
    ]

    return list(db.resenas.aggregate(pipeline))


def horas_pico_restaurante(restaurante_id):
    if isinstance(restaurante_id, str):
        restaurante_id = ObjectId(restaurante_id)

    pipeline = [
        {
            "$match": {
                "restaurante_id": restaurante_id
            }
        },
        {
            "$project": {
                "hora": {"$hour": "$fecha_pedido"},
                "dia_semana": {"$dayOfWeek": "$fecha_pedido"}
            }
        },
        {
            "$group": {
                "_id": {
                    "hora": "$hora",
                    "dia_semana": "$dia_semana"
                },
                "total_ordenes": {"$sum": 1}
            }
        },
        {
            "$project": {
                "_id": 0,
                "hora": "$_id.hora",
                "dia_semana": {
                    "$switch": {
                        "branches": [
                            {"case": {"$eq": ["$_id.dia_semana", 1]}, "then": "Domingo"},
                            {"case": {"$eq": ["$_id.dia_semana", 2]}, "then": "Lunes"},
                            {"case": {"$eq": ["$_id.dia_semana", 3]}, "then": "Martes"},
                            {"case": {"$eq": ["$_id.dia_semana", 4]}, "then": "Miércoles"},
                            {"case": {"$eq": ["$_id.dia_semana", 5]}, "then": "Jueves"},
                            {"case": {"$eq": ["$_id.dia_semana", 6]}, "then": "Viernes"},
                            {"case": {"$eq": ["$_id.dia_semana", 7]}, "then": "Sábado"}
                        ],
                        "default": "Desconocido"
                    }
                },
                "total_ordenes": 1
            }
        },
        {
            "$sort": {
                "total_ordenes": -1,
                "hora": 1
            }
        }
    ]

    return list(db.ordenes.aggregate(pipeline))


def ventas_por_restaurante():
    pipeline = [
        {
            "$group": {
                "_id": "$restaurante_id",
                "ordenes": {"$sum": 1},
                "ventas_totales": {"$sum": {"$toDouble": "$total"}},
                "ticket_promedio": {"$avg": {"$toDouble": "$total"}}
            }
        },
        {
            "$lookup": {
                "from": "restaurantes",
                "localField": "_id",
                "foreignField": "_id",
                "as": "restaurante"
            }
        },
        {
            "$unwind": "$restaurante"
        },
        {
            "$project": {
                "_id": 0,
                "restaurante_id": "$restaurante._id",
                "restaurante": "$restaurante.nombre",
                "ordenes": 1,
                "ventas_totales": {"$round": ["$ventas_totales", 2]},
                "ticket_promedio": {"$round": ["$ticket_promedio", 2]}
            }
        },
        {
            "$sort": {
                "ventas_totales": -1
            }
        }
    ]

    return list(db.ordenes.aggregate(pipeline))


def promedio_gasto_por_usuario(limite=10):
    pipeline = [
        {
            "$group": {
                "_id": "$usuario_id",
                "total_gastado": {"$sum": {"$toDouble": "$total"}},
                "cantidad_ordenes": {"$sum": 1},
                "promedio_gasto": {"$avg": {"$toDouble": "$total"}}
            }
        },
        {
            "$lookup": {
                "from": "usuarios",
                "localField": "_id",
                "foreignField": "_id",
                "as": "usuario"
            }
        },
        {
            "$unwind": "$usuario"
        },
        {
            "$project": {
                "_id": 0,
                "usuario_id": "$usuario._id",
                "nombre": "$usuario.nombre",
                "apellido": "$usuario.apellido",
                "email": "$usuario.email",
                "cantidad_ordenes": 1,
                "total_gastado": {"$round": ["$total_gastado", 2]},
                "promedio_gasto": {"$round": ["$promedio_gasto", 2]}
            }
        },
        {
            "$sort": {
                "promedio_gasto": -1
            }
        },
        {
            "$limit": limite
        }
    ]

    return list(db.ordenes.aggregate(pipeline))