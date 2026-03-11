from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from crud.update import (
    desactivar_usuarios_inactivos,
    aplicar_descuento_por_categoria,
    marcar_ordenes_anticuadas,
)
from crud.delete import (
    limpiar_resenas_antiguas,
    eliminar_usuarios_inactivos,
    limpiar_ordenes_canceladas,
)
from crud.common import client, set_index_enforcement, get_index_enforcement

router = APIRouter(prefix="/admin", tags=["Admin"])


class DiscountPayload(BaseModel):
    categoria: str
    porcentaje_descuento: float


class IndexEnforcementPayload(BaseModel):
    enabled: bool


@router.post("/deactivate-inactive-users")
def deactivate_inactive_users(months: int = Query(6, ge=1, le=60)):
    try:
        count = desactivar_usuarios_inactivos(meses_inactividad=months)
        return {"message": f"{count} usuario(s) desactivados", "modified": count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/apply-category-discount")
def apply_category_discount(payload: DiscountPayload):
    try:
        result = aplicar_descuento_por_categoria(
            categoria=payload.categoria,
            porcentaje_descuento=payload.porcentaje_descuento,
        )
        return {"message": f"Descuento aplicado: {result.get('modified', 0)} artículo(s)", **result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/mark-old-orders")
def mark_old_orders():
    try:
        count = marcar_ordenes_anticuadas()
        return {"message": f"{count} orden(es) marcadas como anticuadas", "modified": count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/old-reviews")
def clean_old_reviews(years: int = Query(2, ge=1, le=20)):
    try:
        count = limpiar_resenas_antiguas(años=years)
        return {"message": f"{count} reseña(s) eliminadas", "deleted": count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/inactive-users")
def clean_inactive_users():
    try:
        count = eliminar_usuarios_inactivos()
        return {"message": f"{count} usuario(s) inactivo(s) eliminados", "deleted": count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/cancelled-orders")
def clean_cancelled_orders():
    try:
        count = limpiar_ordenes_canceladas()
        return {"message": f"{count} orden(es) canceladas eliminadas", "deleted": count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/index-enforcement")
def get_index_enforcement_status():
    return {
        "app_enforcement_enabled": get_index_enforcement(),
        "note": "La política de app bloquea consultas con COLLSCAN cuando hay filtro.",
    }


@router.post("/index-enforcement")
def set_index_enforcement_status(payload: IndexEnforcementPayload):
    app_flag = set_index_enforcement(payload.enabled)
    db_result = {"applied": False, "message": None}

    # Intento opcional de enforcement a nivel servidor (puede fallar en Atlas por permisos).
    try:
        if payload.enabled:
            client.admin.command({"setParameter": 1, "notablescan": True})
        else:
            client.admin.command({"setParameter": 1, "notablescan": False})
        db_result = {"applied": True, "message": "setParameter notablescan aplicado"}
    except Exception as exc:
        db_result = {
            "applied": False,
            "message": f"No se pudo aplicar notablescan a nivel servidor: {exc}",
        }

    return {
        "app_enforcement_enabled": app_flag,
        "db_enforcement": db_result,
    }
