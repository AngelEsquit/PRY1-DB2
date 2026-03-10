from fastapi import APIRouter, HTTPException, Query
from bson import ObjectId

from aggregations.aggregations import (
    platillos_mas_vendidos_mes,
    restaurantes_mejor_calificados,
    horas_pico_restaurante,
    ventas_por_restaurante,
    promedio_gasto_por_usuario,
)

router = APIRouter(prefix="/reports", tags=["Reports"])


def _serialize_object_ids(value):
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, list):
        return [_serialize_object_ids(v) for v in value]
    if isinstance(value, dict):
        return {k: _serialize_object_ids(v) for k, v in value.items()}
    return value


@router.get("/top-dishes")
def get_top_dishes(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    restaurant_id: str | None = None,
    limit: int = Query(10, ge=1, le=100),
):
    try:
        data = platillos_mas_vendidos_mes(
            anio=year,
            mes=month,
            restaurante_id=restaurant_id,
            limite=limit,
        )
        return [_serialize_object_ids(row) for row in data]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/top-rated-restaurants")
def get_top_rated_restaurants(
    min_reviews: int = Query(5, ge=1, le=1000),
    limit: int = Query(10, ge=1, le=100),
):
    try:
        data = restaurantes_mejor_calificados(min_resenas=min_reviews, limite=limit)
        return [_serialize_object_ids(row) for row in data]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/peak-hours")
def get_peak_hours(restaurant_id: str):
    try:
        data = horas_pico_restaurante(restaurante_id=restaurant_id)
        return [_serialize_object_ids(row) for row in data]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sales-by-restaurant")
def get_sales_by_restaurant():
    try:
        data = ventas_por_restaurante()
        return [_serialize_object_ids(row) for row in data]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/avg-spend-per-user")
def get_avg_spend_per_user(limit: int = Query(10, ge=1, le=100)):
    try:
        data = promedio_gasto_por_usuario(limite=limit)
        return [_serialize_object_ids(row) for row in data]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))