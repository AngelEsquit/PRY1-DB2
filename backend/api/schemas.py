from pydantic import BaseModel, Field
from typing import List, Optional


class ReviewCreate(BaseModel):
    usuario_id: str
    restaurante_id: str
    calificacion: int = Field(ge=1, le=5)
    titulo: str
    comentario: str


class OrderItemCreate(BaseModel):
    articulo_id: str
    cantidad: int = Field(ge=1)


class OrderCreate(BaseModel):
    usuario_id: str
    restaurante_id: str
    metodo_pago: str
    items: List[OrderItemCreate]


class MessageResponse(BaseModel):
    message: str