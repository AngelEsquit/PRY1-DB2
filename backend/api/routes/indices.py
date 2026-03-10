from datetime import timedelta
from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from comparacion_indices.comparacion_indices import (
    explain_find,
    summarize_explain,
    extract_search_term,
)
from crud.common import db

router = APIRouter(prefix="/indices", tags=["Indices"])


def _compare(
    label: str,
    collection,
    query_no_idx: Dict[str, Any],
    query_with_idx: Dict[str, Any],
    index_name: str,
) -> Dict[str, Any]:
    no_idx = summarize_explain(
        explain_find(collection, query_no_idx, hint={"$natural": 1})
    )
    if "$text" in query_with_idx:
        with_idx = summarize_explain(explain_find(collection, query_with_idx))
    else:
        with_idx = summarize_explain(
            explain_find(collection, query_with_idx, hint=index_name)
        )
    base = no_idx["time_ms"]
    comp = with_idx["time_ms"]
    if isinstance(base, (int, float)) and base > 0 and isinstance(comp, (int, float)) and comp >= 0:
        mejora = round(((base - comp) / base) * 100, 2)
    else:
        mejora = None
    return {
        "label": label,
        "sin_indice": no_idx,
        "con_indice": with_idx,
        "mejora_pct": mejora,
        "indice_detectado": with_idx.get("index_used") or index_name,
    }


@router.get("/comparison")
def get_index_comparison():
    try:
        usuario = db.usuarios.find_one({}, {"email": 1, "tipo": 1, "puntos": 1})
        orden = db.ordenes.find_one({}, {"usuario_id": 1, "fecha_pedido": 1, "restaurante_id": 1, "estado": 1})
        restaurante = db.restaurantes.find_one({}, {"ubicacion": 1, "nombre": 1, "descripcion": 1, "tipo_comida": 1})
        articulo = db.articulos_menu.find_one({}, {"restaurante_id": 1, "categoria": 1})
        resena = db.resenas.find_one({}, {"restaurante_id": 1, "calificacion_general": 1, "titulo": 1, "comentario": 1})

        if not all([usuario, orden, restaurante, articulo, resena]):
            raise ValueError("No hay suficientes datos para ejecutar la comparación")

        results = []

        # 1) Simple: usuarios.email
        q_email = {"email": usuario["email"]}
        results.append(_compare(
            "1. Índice simple: usuarios.email",
            db.usuarios, q_email, q_email, "idx_usuarios_email_unique",
        ))

        # 2) Compound: usuarios.tipo + puntos
        q_tp = {
            "tipo": usuario.get("tipo", "regular"),
            "puntos": {"$gte": max(int(usuario.get("puntos", 0)) - 50, 0)},
        }
        results.append(_compare(
            "2. Índice compuesto: usuarios.tipo + puntos",
            db.usuarios, q_tp, q_tp, "idx_usuarios_tipo_puntos",
        ))

        # 3) Compound: articulos_menu.restaurante_id + categoria
        q_art = {"restaurante_id": articulo["restaurante_id"], "categoria": articulo["categoria"]}
        results.append(_compare(
            "3. Índice compuesto: articulos_menu.restaurante_id + categoria",
            db.articulos_menu, q_art, q_art, "idx_articulos_restaurante_categoria",
        ))

        # 4) Compound: ordenes.usuario_id + fecha_pedido
        fecha_inicio = orden["fecha_pedido"] - timedelta(days=90)
        q_of = {"usuario_id": orden["usuario_id"], "fecha_pedido": {"$gte": fecha_inicio}}
        results.append(_compare(
            "4. Índice compuesto: ordenes.usuario_id + fecha_pedido",
            db.ordenes, q_of, q_of, "idx_ordenes_usuario_fecha",
        ))

        # 5) Compound: ordenes.restaurante_id + estado
        q_re = {"restaurante_id": orden["restaurante_id"], "estado": orden.get("estado", "pendiente")}
        results.append(_compare(
            "5. Índice compuesto: ordenes.restaurante_id + estado",
            db.ordenes, q_re, q_re, "idx_ordenes_restaurante_estado",
        ))

        # 6) Compound: resenas.restaurante_id + calificacion_general
        q_rc = {"restaurante_id": resena["restaurante_id"], "calificacion_general": resena["calificacion_general"]}
        results.append(_compare(
            "6. Índice compuesto: resenas.restaurante_id + calificacion_general",
            db.resenas, q_rc, q_rc, "idx_resenas_restaurante_calificacion",
        ))

        # 7) Geospatial: restaurantes.ubicacion
        coords = restaurante["ubicacion"].get("coordinates", [-90.5069, 14.6407])
        lon, lat = coords[0], coords[1]
        q_geo = {"ubicacion": {"$geoWithin": {"$centerSphere": [[lon, lat], 5 / 6378.1]}}}
        results.append(_compare(
            "7. Índice geoespacial: restaurantes.ubicacion",
            db.restaurantes, q_geo, q_geo, "idx_restaurantes_ubicacion_geo",
        ))

        # 8) Text index: resenas
        term_r = extract_search_term(
            f"{resena.get('titulo', '')} {resena.get('comentario', '')}"
        )
        q_r_no = {
            "$or": [
                {"titulo": {"$regex": term_r, "$options": "i"}},
                {"comentario": {"$regex": term_r, "$options": "i"}},
            ]
        }
        q_r_with = {"$text": {"$search": term_r}}
        results.append(_compare(
            "8. Índice de texto: resenas.titulo + comentario",
            db.resenas, q_r_no, q_r_with, "idx_resenas_texto",
        ))

        # 9) Text index: restaurantes
        tipos = restaurante.get("tipo_comida") or []
        tipo_token = tipos[0] if tipos else "Comida"
        term_rest = extract_search_term(
            f"{restaurante.get('nombre', '')} {restaurante.get('descripcion', '')} {tipo_token}"
        )
        q_rest_no = {
            "$or": [
                {"nombre": {"$regex": term_rest, "$options": "i"}},
                {"descripcion": {"$regex": term_rest, "$options": "i"}},
                {"tipo_comida": {"$elemMatch": {"$regex": term_rest, "$options": "i"}}},
            ]
        }
        q_rest_with = {"$text": {"$search": term_rest}}
        results.append(_compare(
            "9. Índice de texto: restaurantes.nombre + descripcion + tipo_comida",
            db.restaurantes, q_rest_no, q_rest_with, "idx_restaurantes_texto",
        ))

        return {
            "results": results,
            "tip": "Ejecuta varias veces para ver variaciones por caché caliente/fría.",
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
