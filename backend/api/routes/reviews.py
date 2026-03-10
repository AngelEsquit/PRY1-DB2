from fastapi import APIRouter, HTTPException
from bson import ObjectId

from crud.common import db
from crud.create import crear_resena
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
                "fecha": 1,
            },
        ).sort("fecha", -1).limit(50)
    )

    for r in resenas:
        r["_id"] = str(r["_id"])
        r["usuario_id"] = str(r["usuario_id"])
        r["restaurante_id"] = str(r["restaurante_id"])

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