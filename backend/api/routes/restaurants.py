from fastapi import APIRouter, HTTPException
from bson import ObjectId

from crud.common import db

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])


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

    for r in restaurantes:
        r["_id"] = str(r["_id"])

    return restaurantes


@router.get("/{restaurant_id}")
def get_restaurant_detail(restaurant_id: str):
    try:
        oid = ObjectId(restaurant_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID de restaurante inválido")

    restaurante = db.restaurantes.find_one({"_id": oid})
    if not restaurante:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")

    restaurante["_id"] = str(restaurante["_id"])

    articulos = list(
        db.articulos_menu.find(
            {"restaurante_id": oid},
            {
                "nombre": 1,
                "descripcion": 1,
                "categoria": 1,
                "precio": 1,
                "disponible": 1,
            },
        )
    )

    for a in articulos:
        a["_id"] = str(a["_id"])
        a["restaurante_id"] = str(a["restaurante_id"])
        if "precio" in a:
            a["precio"] = str(a["precio"])

    restaurante["menu"] = articulos
    return restaurante