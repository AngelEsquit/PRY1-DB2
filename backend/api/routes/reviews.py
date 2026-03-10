from fastapi import APIRouter, HTTPException
from bson import ObjectId

from crud.common import db
from crud.create import crear_resena
from crud.delete import eliminar_resena
from api.schemas import ReviewCreate

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.get("/")
def get_reviews():
    resenas = list(
        db.resenas.find(
            {},
            {
                "usuario_id": 1,
                "restaurante_id": 1,
                "titulo": 1,
                "comentario": 1,
                "calificacion_general": 1,
                "fecha_resena": 1,
            },
        ).sort("fecha_resena", -1).limit(50)
    )

    for r in resenas:
        usuario = db.usuarios.find_one({"_id": r.get("usuario_id")}, {"nombre": 1, "apellido": 1})
        restaurante = db.restaurantes.find_one({"_id": r.get("restaurante_id")}, {"nombre": 1})

        r["_id"] = str(r["_id"])
        r["usuario_id"] = str(r["usuario_id"])
        r["restaurante_id"] = str(r["restaurante_id"])
        r["usuario_nombre"] = (
            f"{usuario.get('nombre', '')} {usuario.get('apellido', '')}".strip()
            if usuario
            else "Usuario"
        )
        r["restaurante_nombre"] = restaurante.get("nombre") if restaurante else "Restaurante"

    return resenas


@router.post("/")
def create_review(payload: ReviewCreate):
    try:
        review_id = crear_resena(
            usuario_id=ObjectId(payload.usuario_id),
            restaurante_id=ObjectId(payload.restaurante_id),
            calificacion=payload.calificacion,
            titulo=payload.titulo,
            comentario=payload.comentario,
            db=db,
        )
        return {"message": "Reseña creada con éxito", "review_id": str(review_id)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{review_id}")
def delete_review(review_id: str):
    try:
        count = eliminar_resena(ObjectId(review_id), db=db)
        if count == 0:
            raise HTTPException(status_code=404, detail="Reseña no encontrada")
        return {"message": "Reseña eliminada"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/")
def get_reviews():
    resenas = list(
        db.resenas.find(
            {},
            {
                "usuario_id": 1,
                "restaurante_id": 1,
                "titulo": 1,
                "comentario": 1,
                "calificacion_general": 1,
                "fecha_resena": 1,
            },
        ).sort("fecha_resena", -1).limit(50)
    )

    for r in resenas:
        usuario = db.usuarios.find_one({"_id": r.get("usuario_id")}, {"nombre": 1, "apellido": 1})
        restaurante = db.restaurantes.find_one({"_id": r.get("restaurante_id")}, {"nombre": 1})

        r["_id"] = str(r["_id"])
        r["usuario_id"] = str(r["usuario_id"])
        r["restaurante_id"] = str(r["restaurante_id"])
        r["usuario_nombre"] = (
            f"{usuario.get('nombre', '')} {usuario.get('apellido', '')}".strip()
            if usuario
            else "Usuario"
        )
        r["restaurante_nombre"] = restaurante.get("nombre") if restaurante else "Restaurante"

    return resenas


@router.post("/")
def create_review(payload: ReviewCreate):
    try:
        review_id = crear_resena(
            usuario_id=ObjectId(payload.usuario_id),
            restaurante_id=ObjectId(payload.restaurante_id),
            calificacion=payload.calificacion,
            titulo=payload.titulo,
            comentario=payload.comentario,
            db=db,
        )
        return {"message": "Reseña creada con éxito", "review_id": str(review_id)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))