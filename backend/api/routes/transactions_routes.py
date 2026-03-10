from fastapi import APIRouter, HTTPException
from bson import ObjectId

from transactions.transactions import eliminar_usuario_con_dependencias

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.delete("/users/{user_id}")
def delete_user_with_cascade(user_id: str):
    """Elimina usuario + todas sus órdenes y reseñas en una sola transacción."""
    try:
        result = eliminar_usuario_con_dependencias(ObjectId(user_id))
        return {
            "ok": result.get("ok", False),
            "usuario_eliminado": result.get("usuario_eliminado", 0),
            "ordenes_eliminadas": result.get("ordenes_eliminadas", 0),
            "resenas_eliminadas": result.get("resenas_eliminadas", 0),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
