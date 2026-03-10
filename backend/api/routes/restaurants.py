from fastapi import APIRouter, HTTPException
from bson import ObjectId
from bson.decimal128 import Decimal128

from crud.common import db
from crud.create import crear_restaurante, crear_articulo_menu
from crud.update import actualizar_telefono_restaurante, actualizar_precio_articulo
from crud.delete import eliminar_articulo_menu
from api.schemas import RestaurantCreate, MenuItemCreate, UpdatePhoneRequest, UpdatePriceRequest

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])


def serialize_decimal(value):
    if isinstance(value, Decimal128):
        return float(value.to_decimal())
    return value


@router.get("/")
def get_restaurants():
    restaurantes = list(
        db.restaurantes.find(
            {},
            {
                "nombre": 1,
                "descripcion": 1,
                "tipo_comida": 1,
                "direccion": 1,
                "telefono": 1,
                "email": 1,
            },
        ).limit(50)
    )

    resultado = []
    for r in restaurantes:
        resultado.append(
            {
                "_id": str(r.get("_id")),
                "nombre": r.get("nombre"),
                "descripcion": r.get("descripcion"),
                "tipo_comida": r.get("tipo_comida", []),
                "direccion": r.get("direccion", {}),
                "telefono": r.get("telefono"),
                "email": r.get("email"),
            }
        )

    return resultado


@router.post("/")
def create_restaurant(payload: RestaurantCreate):
    try:
        rest_id = crear_restaurante(
            {
                "nombre": payload.nombre,
                "descripcion": payload.descripcion,
                "tipo_comida": payload.tipo_comida,
                "direccion": {"ciudad": payload.ciudad},
                "ubicacion": {"type": "Point", "coordinates": [-90.5069, 14.6407]},
                "horario": [],
                "telefono": payload.telefono,
                "email": payload.email,
            },
            db=db,
        )
        return {"message": "Restaurante creado", "restaurant_id": str(rest_id)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{restaurant_id}/phone")
def update_restaurant_phone(restaurant_id: str, payload: UpdatePhoneRequest):
    try:
        count = actualizar_telefono_restaurante(ObjectId(restaurant_id), payload.nuevo_telefono, db=db)
        if count == 0:
            raise HTTPException(status_code=404, detail="Restaurante no encontrado o sin cambios")
        return {"message": "Teléfono actualizado", "modified": count}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{restaurant_id}")
def delete_restaurant(restaurant_id: str):
    try:
        oid = ObjectId(restaurant_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID de restaurante inválido")

    result = db.restaurantes.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")
    return {"message": "Restaurante eliminado"}


@router.get("/{restaurant_id}")
def get_restaurant_detail(restaurant_id: str):
    try:
        oid = ObjectId(restaurant_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID de restaurante inválido")

    restaurante = db.restaurantes.find_one({"_id": oid})

    if not restaurante:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")

    articulos = list(
        db.articulos_menu.find(
            {"restaurante_id": oid},
            {
                "_id": 1,
                "nombre": 1,
                "descripcion": 1,
                "categoria": 1,
                "precio": 1,
                "disponible": 1,
                "restaurante_id": 1,
            },
        )
    )

    menu = []
    for a in articulos:
        menu.append(
            {
                "_id": str(a.get("_id")),
                "restaurante_id": str(a.get("restaurante_id")) if a.get("restaurante_id") else None,
                "nombre": a.get("nombre"),
                "descripcion": a.get("descripcion"),
                "categoria": a.get("categoria"),
                "precio": serialize_decimal(a.get("precio")),
                "disponible": a.get("disponible", True),
            }
        )

    resultado = {
        "_id": str(restaurante.get("_id")),
        "nombre": restaurante.get("nombre"),
        "descripcion": restaurante.get("descripcion"),
        "tipo_comida": restaurante.get("tipo_comida", []),
        "direccion": restaurante.get("direccion", {}),
        "telefono": restaurante.get("telefono"),
        "email": restaurante.get("email"),
        "menu": menu,
    }

    return resultado


@router.post("/{restaurant_id}/menu")
def create_menu_item(restaurant_id: str, payload: MenuItemCreate):
    try:
        item_id = crear_articulo_menu(
            restaurante_id=ObjectId(restaurant_id),
            datos_articulo={
                "nombre": payload.nombre,
                "descripcion": payload.descripcion,
                "categoria": payload.categoria,
                "precio": payload.precio,
                "ingredientes": payload.ingredientes,
                "opciones_personalizacion": payload.opciones_personalizacion,
                "tiempo_preparacion": payload.tiempo_preparacion,
            },
            db=db,
        )
        return {"message": "Artículo de menú creado", "item_id": str(item_id)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/items/{item_id}/price")
def update_menu_item_price(item_id: str, payload: UpdatePriceRequest):
    try:
        count = actualizar_precio_articulo(ObjectId(item_id), payload.nuevo_precio, db=db)
        if count == 0:
            raise HTTPException(status_code=404, detail="Artículo no encontrado o sin cambios")
        return {"message": "Precio actualizado", "modified": count}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/items/{item_id}")
def delete_menu_item(item_id: str):
    try:
        count = eliminar_articulo_menu(ObjectId(item_id), db=db)
        if count == 0:
            raise HTTPException(status_code=404, detail="Artículo no encontrado")
        return {"message": "Artículo eliminado"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    restaurantes = list(
        db.restaurantes.find(
            {},
            {
                "nombre": 1,
                "descripcion": 1,
                "tipo_comida": 1,
                "direccion": 1,
                "telefono": 1,
                "email": 1,
            },
        ).limit(50)
    )

    resultado = []
    for r in restaurantes:
        resultado.append(
            {
                "_id": str(r.get("_id")),
                "nombre": r.get("nombre"),
                "descripcion": r.get("descripcion"),
                "tipo_comida": r.get("tipo_comida", []),
                "direccion": r.get("direccion", {}),
                "telefono": r.get("telefono"),
                "email": r.get("email"),
            }
        )

    return resultado


@router.get("/{restaurant_id}")
def get_restaurant_detail(restaurant_id: str):
    try:
        oid = ObjectId(restaurant_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID de restaurante inválido")

    restaurante = db.restaurantes.find_one({"_id": oid})

    if not restaurante:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")

    articulos = list(
        db.articulos_menu.find(
            {"restaurante_id": oid},
            {
                "_id": 1,
                "nombre": 1,
                "descripcion": 1,
                "categoria": 1,
                "precio": 1,
                "disponible": 1,
                "restaurante_id": 1,
            },
        )
    )

    menu = []
    for a in articulos:
        menu.append(
            {
                "_id": str(a.get("_id")),
                "restaurante_id": str(a.get("restaurante_id")) if a.get("restaurante_id") else None,
                "nombre": a.get("nombre"),
                "descripcion": a.get("descripcion"),
                "categoria": a.get("categoria"),
                "precio": serialize_decimal(a.get("precio")),
                "disponible": a.get("disponible", True),
            }
        )

    resultado = {
        "_id": str(restaurante.get("_id")),
        "nombre": restaurante.get("nombre"),
        "descripcion": restaurante.get("descripcion"),
        "tipo_comida": restaurante.get("tipo_comida", []),
        "direccion": restaurante.get("direccion", {}),
        "telefono": restaurante.get("telefono"),
        "email": restaurante.get("email"),
        "menu": menu,
    }

    return resultado