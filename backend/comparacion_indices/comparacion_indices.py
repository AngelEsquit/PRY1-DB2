import re
from datetime import timedelta
from typing import Any, Dict, Optional

from pymongo.errors import PyMongoError
from pymongo.database import Database

from crud.common import get_db, load_dotenv_file


def get_indexes_map(db: Database) -> Dict[str, Dict[str, Any]]:
    return {
        "usuarios": db.usuarios.index_information(),
        "ordenes": db.ordenes.index_information(),
        "articulos_menu": db.articulos_menu.index_information(),
        "resenas": db.resenas.index_information(),
        "restaurantes": db.restaurantes.index_information(),
    }


def find_used_index(plan: Dict[str, Any]) -> Optional[str]:
    if not isinstance(plan, dict):
        return None

    if "indexName" in plan:
        return plan["indexName"]

    for key in ["inputStage", "outerStage", "innerStage", "queryPlan", "winningPlan"]:
        if key in plan:
            idx = find_used_index(plan[key])
            if idx:
                return idx

    for key in ["shards", "inputStages", "children"]:
        value = plan.get(key)
        if isinstance(value, list):
            for entry in value:
                idx = find_used_index(entry)
                if idx:
                    return idx

    return None


def explain_find(collection, query: Dict[str, Any], hint=None) -> Dict[str, Any]:
    find_command: Dict[str, Any] = {
        "find": collection.name,
        "filter": query,
    }

    if hint is not None:
        find_command["hint"] = hint

    return collection.database.command("explain", find_command, verbosity="executionStats")


def summarize_explain(explain_doc: Dict[str, Any]) -> Dict[str, Any]:
    exec_stats = explain_doc.get("executionStats", {})
    planner = explain_doc.get("queryPlanner", {})
    winning_plan = planner.get("winningPlan", {})

    return {
        "time_ms": exec_stats.get("executionTimeMillis", -1),
        "docs_examined": exec_stats.get("totalDocsExamined", -1),
        "keys_examined": exec_stats.get("totalKeysExamined", -1),
        "index_used": find_used_index(winning_plan),
    }


def print_case(title: str, no_idx: Dict[str, Any], with_idx: Dict[str, Any], expected_index: str) -> None:
    print(f"\n{title}")
    print("-" * len(title))
    print(
        f"SIN indice  -> tiempo: {no_idx['time_ms']} ms | "
        f"docs: {no_idx['docs_examined']} | keys: {no_idx['keys_examined']}"
    )
    print(
        f"CON indice  -> tiempo: {with_idx['time_ms']} ms | "
        f"docs: {with_idx['docs_examined']} | keys: {with_idx['keys_examined']}"
    )

    base = no_idx["time_ms"]
    comp = with_idx["time_ms"]
    if isinstance(base, (int, float)) and base > 0 and isinstance(comp, (int, float)) and comp >= 0:
        improvement = ((base - comp) / base) * 100
        print(f"Mejora estimada: {improvement:.2f}%")
    else:
        print("Mejora estimada: n/a")

    idx_name = with_idx.get("index_used") or expected_index
    print(f"Indice detectado en plan: {idx_name}")


def extract_search_term(text: str) -> str:
    if not text:
        return "restaurante"
    words = re.findall(r"[A-Za-zÁÉÍÓÚáéíóúÑñ]{4,}", text)
    return words[0] if words else "restaurante"


def compare_index(
    title: str,
    collection,
    query_without_index: Dict[str, Any],
    query_with_index: Dict[str, Any],
    index_name: str,
) -> None:
    no_idx_explain = explain_find(collection, query_without_index, hint={"$natural": 1})

    if "$text" in query_with_index:
        with_idx_explain = explain_find(collection, query_with_index)
    else:
        with_idx_explain = explain_find(collection, query_with_index, hint=index_name)

    print_case(
        title,
        summarize_explain(no_idx_explain),
        summarize_explain(with_idx_explain),
        index_name,
    )


def presentacion_indices(db: Database) -> None:
    print("\n" + "=" * 72)
    print("DEMO DE RENDIMIENTO DE INDICES (MongoDB)")
    print("=" * 72)

    indexes = get_indexes_map(db)

    needed = {
        "usuarios": "idx_usuarios_email_unique",
        "usuarios_tipo": "idx_usuarios_tipo_puntos",
        "articulos_menu": "idx_articulos_restaurante_categoria",
        "ordenes": "idx_ordenes_usuario_fecha",
        "ordenes_estado": "idx_ordenes_restaurante_estado",
        "resenas": "idx_resenas_restaurante_calificacion",
        "resenas_texto": "idx_resenas_texto",
        "restaurantes": "idx_restaurantes_ubicacion_geo",
        "restaurantes_multikey": "idx_restaurantes_tipo_comida_multikey",
        "restaurantes_texto": "idx_restaurantes_texto",
    }

    collection_for_key = {
        "usuarios": "usuarios",
        "usuarios_tipo": "usuarios",
        "articulos_menu": "articulos_menu",
        "ordenes": "ordenes",
        "ordenes_estado": "ordenes",
        "resenas": "resenas",
        "resenas_texto": "resenas",
        "restaurantes": "restaurantes",
        "restaurantes_multikey": "restaurantes",
        "restaurantes_texto": "restaurantes",
    }

    for key, idx_name in needed.items():
        coll = collection_for_key[key]
        if idx_name not in indexes[coll]:
            raise ValueError(
                f"No se encontro el indice '{idx_name}' en '{coll}'. "
                "Ejecuta primero el generador para crear indices."
            )

    usuario = db.usuarios.find_one({}, {"email": 1})
    if not usuario or "email" not in usuario:
        raise ValueError("No hay usuarios para realizar la comparacion por email.")

    orden = db.ordenes.find_one({}, {"usuario_id": 1, "fecha_pedido": 1})
    if not orden or "usuario_id" not in orden or "fecha_pedido" not in orden:
        raise ValueError("No hay ordenes para realizar la comparacion compuesta.")

    restaurante = db.restaurantes.find_one({}, {"ubicacion": 1})
    if not restaurante or "ubicacion" not in restaurante:
        raise ValueError("No hay restaurantes para realizar la comparacion geoespacial.")

    usuario_tipo = db.usuarios.find_one({}, {"tipo": 1, "puntos": 1})
    if not usuario_tipo or "tipo" not in usuario_tipo or "puntos" not in usuario_tipo:
        raise ValueError("No hay usuarios para realizar la comparacion por tipo+puntos.")

    articulo = db.articulos_menu.find_one({}, {"restaurante_id": 1, "categoria": 1})
    if not articulo or "restaurante_id" not in articulo or "categoria" not in articulo:
        raise ValueError("No hay articulos para realizar la comparacion por restaurante+categoria.")

    orden_estado = db.ordenes.find_one({}, {"restaurante_id": 1, "estado": 1})
    if not orden_estado or "restaurante_id" not in orden_estado or "estado" not in orden_estado:
        raise ValueError("No hay ordenes para realizar la comparacion por restaurante+estado.")

    resena = db.resenas.find_one({}, {"restaurante_id": 1, "calificacion_general": 1, "titulo": 1, "comentario": 1})
    if not resena or "restaurante_id" not in resena or "calificacion_general" not in resena:
        raise ValueError("No hay resenas para realizar la comparacion por restaurante+calificacion.")

    restaurante_texto = db.restaurantes.find_one({}, {"nombre": 1, "descripcion": 1, "tipo_comida": 1})
    if not restaurante_texto:
        raise ValueError("No hay restaurantes para realizar la comparacion de texto.")

    query_email = {"email": usuario["email"]}
    compare_index(
        "1) Indice simple: usuarios.email",
        db.usuarios,
        query_email,
        query_email,
        "idx_usuarios_email_unique",
    )

    query_tipo_puntos = {
        "tipo": usuario_tipo["tipo"],
        "puntos": {"$gte": max(int(usuario_tipo["puntos"]) - 50, 0)},
    }
    compare_index(
        "2) Indice compuesto: usuarios.tipo + puntos",
        db.usuarios,
        query_tipo_puntos,
        query_tipo_puntos,
        "idx_usuarios_tipo_puntos",
    )

    query_articulos = {
        "restaurante_id": articulo["restaurante_id"],
        "categoria": articulo["categoria"],
    }
    compare_index(
        "3) Indice compuesto: articulos_menu.restaurante_id + categoria",
        db.articulos_menu,
        query_articulos,
        query_articulos,
        "idx_articulos_restaurante_categoria",
    )

    fecha_inicio = orden["fecha_pedido"] - timedelta(days=90)
    query_compuesto = {
        "usuario_id": orden["usuario_id"],
        "fecha_pedido": {"$gte": fecha_inicio},
    }
    compare_index(
        "4) Indice compuesto: ordenes.usuario_id + fecha_pedido",
        db.ordenes,
        query_compuesto,
        query_compuesto,
        "idx_ordenes_usuario_fecha",
    )

    query_rest_estado = {
        "restaurante_id": orden_estado["restaurante_id"],
        "estado": orden_estado["estado"],
    }
    compare_index(
        "5) Indice compuesto: ordenes.restaurante_id + estado",
        db.ordenes,
        query_rest_estado,
        query_rest_estado,
        "idx_ordenes_restaurante_estado",
    )

    query_resena_comp = {
        "restaurante_id": resena["restaurante_id"],
        "calificacion_general": resena["calificacion_general"],
    }
    compare_index(
        "6) Indice compuesto: resenas.restaurante_id + calificacion_general",
        db.resenas,
        query_resena_comp,
        query_resena_comp,
        "idx_resenas_restaurante_calificacion",
    )

    coords = restaurante["ubicacion"].get("coordinates", [-90.5, 14.6])
    lon, lat = coords[0], coords[1]
    query_geo = {
        "ubicacion": {
            "$geoWithin": {
                "$centerSphere": [[lon, lat], 5 / 6378.1],
            }
        }
    }
    compare_index(
        "7) Indice geoespacial: restaurantes.ubicacion",
        db.restaurantes,
        query_geo,
        query_geo,
        "idx_restaurantes_ubicacion_geo",
    )

    rare_tipo_doc = next(
        db.restaurantes.aggregate(
            [
                {"$unwind": "$tipo_comida"},
                {"$group": {"_id": "$tipo_comida", "count": {"$sum": 1}}},
                {"$sort": {"count": 1}},
                {"$limit": 1},
            ]
        ),
        None,
    )
    tipos_disponibles = restaurante_texto.get("tipo_comida") or []
    tipo_multikey = (
        rare_tipo_doc.get("_id")
        if rare_tipo_doc and rare_tipo_doc.get("_id")
        else (tipos_disponibles[0] if tipos_disponibles else "Comida")
    )
    query_multikey = {"tipo_comida": tipo_multikey}
    compare_index(
        "8) Indice multikey: restaurantes.tipo_comida",
        db.restaurantes,
        query_multikey,
        query_multikey,
        "idx_restaurantes_tipo_comida_multikey",
    )

    term_resena = extract_search_term(f"{resena.get('titulo', '')} {resena.get('comentario', '')}")
    text_query_resena = {"$text": {"$search": term_resena}}
    regex_query_resena = {
        "$or": [
            {"titulo": {"$regex": term_resena, "$options": "i"}},
            {"comentario": {"$regex": term_resena, "$options": "i"}},
        ]
    }
    compare_index(
        "9) Indice de texto: resenas.titulo + comentario",
        db.resenas,
        regex_query_resena,
        text_query_resena,
        "idx_resenas_texto",
    )

    tipos = restaurante_texto.get("tipo_comida") or []
    tipo_token = tipos[0] if tipos else "Comida"
    term_rest = extract_search_term(
        f"{restaurante_texto.get('nombre', '')} {restaurante_texto.get('descripcion', '')} {tipo_token}"
    )
    text_query_rest = {"$text": {"$search": term_rest}}
    regex_query_rest = {
        "$or": [
            {"nombre": {"$regex": term_rest, "$options": "i"}},
            {"descripcion": {"$regex": term_rest, "$options": "i"}},
            {"tipo_comida": {"$elemMatch": {"$regex": term_rest, "$options": "i"}}},
        ]
    }
    compare_index(
        "10) Indice de texto: restaurantes.nombre + descripcion + tipo_comida",
        db.restaurantes,
        regex_query_rest,
        text_query_rest,
        "idx_restaurantes_texto",
    )

    print("\n" + "=" * 72)
    print("Tip: ejecuta el script 2-3 veces para ver variaciones por cache caliente/fria.")
    print("=" * 72)


def main() -> None:
    try:
        load_dotenv_file()
        db = get_db()
        print(f"Conectado a base de datos: {db.name}")
        presentacion_indices(db)
    except PyMongoError as exc:
        print(f"Error de MongoDB: {exc}")
        raise
    except Exception as exc:
        print(f"Error: {exc}")
        raise


if __name__ == "__main__":
    main()