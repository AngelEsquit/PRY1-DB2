from fastapi import APIRouter, HTTPException
from bson import ObjectId
from pydantic import BaseModel
from typing import Optional

from arrays.arrays import (
    agregar_preferencia_usuario,
    eliminar_preferencia_usuario,
    agregar_horario_restaurante,
    agregar_respuesta_resena,
    eliminar_respuesta_resena,
)

router = APIRouter(prefix="/arrays", tags=["Arrays"])


class PreferenciaPayload(BaseModel):
    usuario_id: str
    preferencia: str


class HorarioPayload(BaseModel):
    restaurante_id: str
    dia: str
    apertura: str
    cierre: str


class RespuestaPayload(BaseModel):
    resena_id: str
    texto: str
    autor: Optional[str] = "Restaurante"


class EliminarRespuestaPayload(BaseModel):
    resena_id: str
    texto: str


@router.post("/preferences/add")
def add_preference(payload: PreferenciaPayload):
    try:
        result = agregar_preferencia_usuario(
            ObjectId(payload.usuario_id), payload.preferencia
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/preferences/remove")
def remove_preference(payload: PreferenciaPayload):
    try:
        result = eliminar_preferencia_usuario(
            ObjectId(payload.usuario_id), payload.preferencia
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/schedule/add")
def add_schedule(payload: HorarioPayload):
    try:
        horario = {"dia": payload.dia, "apertura": payload.apertura, "cierre": payload.cierre}
        result = agregar_horario_restaurante(
            ObjectId(payload.restaurante_id), horario
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/reviews/reply/add")
def add_reply(payload: RespuestaPayload):
    try:
        respuesta = {"texto": payload.texto, "autor": payload.autor}
        result = agregar_respuesta_resena(ObjectId(payload.resena_id), respuesta)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/reviews/reply/remove")
def remove_reply(payload: EliminarRespuestaPayload):
    try:
        result = eliminar_respuesta_resena(ObjectId(payload.resena_id), payload.texto)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
