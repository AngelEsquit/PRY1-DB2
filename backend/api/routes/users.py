from fastapi import APIRouter, HTTPException, Query

from bson import ObjectId

from crud.common import db
from crud.create import crear_usuario
from crud.update import actualizar_email_usuario
from crud.delete import eliminar_usuario
from api.schemas import UserCreate, UpdateEmailRequest

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/")
def get_users(tipo: str | None = None):
    filtro = {}
    if tipo:
        filtro["tipo"] = tipo
    usuarios = list(
        db.usuarios.find(
            filtro,
            {
                "nombre": 1,
                "apellido": 1,
                "email": 1,
                "tipo": 1,
                "puntos": 1,
                "activo": 1,
            },
        ).limit(200)
    )

    resultado = []
    for usuario in usuarios:
        resultado.append(
            {
                "_id": str(usuario.get("_id")),
                "nombre": usuario.get("nombre"),
                "apellido": usuario.get("apellido"),
                "email": usuario.get("email"),
                "tipo": usuario.get("tipo"),
                "puntos": usuario.get("puntos", 0),
                "activo": usuario.get("activo", True),
            }
        )

    return resultado


@router.get("/{user_id}")
def get_user(user_id: str):
    try:
        oid = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID de usuario inválido")

    usuario = db.usuarios.find_one({"_id": oid})
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario["_id"] = str(usuario["_id"])
    for fk in ("restaurante_id",):
        if fk in usuario and isinstance(usuario[fk], ObjectId):
            usuario[fk] = str(usuario[fk])
    return usuario


@router.post("/")
def create_user(payload: UserCreate):
    try:
        user_id = crear_usuario(
            nombre=payload.nombre,
            apellido=payload.apellido,
            email=payload.email,
            telefono=payload.telefono,
            direccion={"ciudad": payload.ciudad},
            db=db,
        )
        return {"message": "Usuario creado", "user_id": str(user_id)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{user_id}/email")
def update_user_email(user_id: str, payload: UpdateEmailRequest):
    try:
        count = actualizar_email_usuario(ObjectId(user_id), payload.nuevo_email, db=db)
        if count == 0:
            raise HTTPException(status_code=404, detail="Usuario no encontrado o sin cambios")
        return {"message": "Email actualizado", "modified": count}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}")
def delete_user(user_id: str):
    try:
        count = eliminar_usuario(ObjectId(user_id), db=db)
        if count == 0:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return {"message": "Usuario eliminado", "deleted": count}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))