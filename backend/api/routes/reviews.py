from fastapi import APIRouter, HTTPException, Query
from bson import ObjectId

from crud.common import db, ensure_indexed_query
from crud.create import crear_resena
from crud.delete import eliminar_resena
from api.schemas import ReviewCreate, ReviewUpdate

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.get("/")
def get_reviews(
    restaurante_id: str | None = None,
    min_calificacion: int | None = Query(None, ge=1, le=5),
    max_calificacion: int | None = Query(None, ge=1, le=5),
    sort_by: str = Query("fecha_resena"),
    sort_dir: int = Query(-1),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    filtro = {}
    if restaurante_id:
        try:
            filtro["restaurante_id"] = ObjectId(restaurante_id)
        except Exception:
            raise HTTPException(status_code=400, detail="ID de restaurante inválido")

    if min_calificacion is not None or max_calificacion is not None:
        rango = {}
        if min_calificacion is not None:
            rango["$gte"] = min_calificacion
        if max_calificacion is not None:
            rango["$lte"] = max_calificacion
        filtro["calificacion_general"] = rango

    ensure_indexed_query(db.resenas, filtro)
    sort_direction = 1 if sort_dir >= 0 else -1

    resenas = list(
        db.resenas.find(
            filtro,
            {
                "usuario_id": 1,
                "restaurante_id": 1,
                "titulo": 1,
                "comentario": 1,
                "calificacion_general": 1,
                "fecha_resena": 1,
            },
        ).sort(sort_by, sort_direction).skip(skip).limit(limit)
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


@router.patch("/{review_id}")
def update_review(review_id: str, payload: ReviewUpdate):
    try:
        oid = ObjectId(review_id)
        result = db.resenas.update_one(
            {"_id": oid},
            {
                "$set": {
                    "calificacion_general": payload.calificacion,
                    "titulo": payload.titulo,
                    "comentario": payload.comentario,
                }
            },
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Reseña no encontrada")
        return {"message": "Reseña actualizada", "modified": result.modified_count}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))