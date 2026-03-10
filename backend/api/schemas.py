from pydantic import BaseModel, EmailStr, Field
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


# ── CRUD schemas ──────────────────────────────────────────────────

class UserCreate(BaseModel):
    nombre: str
    apellido: str
    email: str
    telefono: str
    ciudad: str = "Guatemala"


class RestaurantCreate(BaseModel):
    nombre: str
    descripcion: str
    tipo_comida: List[str]
    telefono: str
    email: str
    ciudad: str = "Guatemala"


class MenuItemCreate(BaseModel):
    nombre: str
    descripcion: str
    categoria: str
    precio: float = Field(gt=0)
    ingredientes: List[str] = []
    opciones_personalizacion: List[str] = []
    tiempo_preparacion: int = Field(default=15, ge=1)


class UpdateEmailRequest(BaseModel):
    nuevo_email: str


class UpdatePhoneRequest(BaseModel):
    nuevo_telefono: str


class UpdatePriceRequest(BaseModel):
    nuevo_precio: float = Field(gt=0)


class UpdateStatusRequest(BaseModel):
    nuevo_estado: str