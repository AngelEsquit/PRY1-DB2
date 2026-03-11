import os
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Dict, Optional
from dotenv import load_dotenv

from bson import Decimal128, ObjectId
from pymongo import MongoClient
from pymongo.database import Database


DEFAULT_DB_NAME = "restaurantes_db"
VALID_USER_TYPES = {"regular", "premium", "vip"}
VALID_ORDER_STATES = {
    "pendiente",
    "confirmado",
    "en_preparacion",
    "en_camino",
    "entregado",
    "cancelado",
    "archivada",
}

ORDER_STATE_TRANSITIONS = {
    "pendiente": {"confirmado", "cancelado"},
    "confirmado": {"en_preparacion", "cancelado"},
    "en_preparacion": {"en_camino", "cancelado"},
    "en_camino": {"entregado", "cancelado"},
    "entregado": {"archivada"},
    "cancelado": {"archivada"},
    "archivada": set(),
}

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=ENV_PATH)

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", DEFAULT_DB_NAME)
client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]
INDEX_ENFORCEMENT_ENABLED = os.getenv("ENFORCE_INDEX_USAGE", "false").lower() == "true"


def load_dotenv_file(path: str = str(ENV_PATH)) -> None:
    if not os.path.exists(path):
        return

    with open(path, "r", encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def get_db() -> Database:
    load_dotenv_file()
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise ValueError("La variable de entorno MONGO_URI es obligatoria.")

    db_name = os.getenv("MONGO_DB_NAME", DEFAULT_DB_NAME)
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=20000)
    client.admin.command("ping")
    return client[db_name]


def resolve_db(db: Optional[Database]) -> Database:
    return db if db is not None else get_db()


def to_object_id(value: Any, field_name: str) -> ObjectId:
    if isinstance(value, ObjectId):
        return value
    if isinstance(value, str) and ObjectId.is_valid(value):
        return ObjectId(value)
    raise ValueError(f"{field_name} no es un ObjectId valido")


def quantize_money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def to_decimal128(value: Any) -> Decimal128:
    if isinstance(value, Decimal128):
        return value
    if isinstance(value, Decimal):
        return Decimal128(str(quantize_money(value)))
    if isinstance(value, (int, float, str)):
        return Decimal128(str(quantize_money(Decimal(str(value)))))
    raise ValueError("No se pudo convertir el valor a Decimal128")


def to_decimal(value: Any) -> Decimal:
    if isinstance(value, Decimal128):
        return value.to_decimal()
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _plan_has_collscan(plan: Dict[str, Any]) -> bool:
    if not isinstance(plan, dict):
        return False

    if plan.get("stage") == "COLLSCAN":
        return True

    for key in ["inputStage", "outerStage", "innerStage", "queryPlan", "winningPlan"]:
        if key in plan and _plan_has_collscan(plan[key]):
            return True

    for key in ["shards", "inputStages", "children"]:
        value = plan.get(key)
        if isinstance(value, list):
            for entry in value:
                if _plan_has_collscan(entry):
                    return True

    return False


def ensure_indexed_query(collection, filter_query: Optional[Dict[str, Any]] = None) -> None:
    """
    Rechaza consultas con COLLSCAN cuando ENFORCE_INDEX_USAGE está activo.
    Para evitar bloquear listados base, no valida filtros vacíos.
    """
    if not INDEX_ENFORCEMENT_ENABLED:
        return

    if not filter_query:
        return

    explain_doc = collection.database.command(
        "explain",
        {"find": collection.name, "filter": filter_query},
        verbosity="queryPlanner",
    )
    winning_plan = explain_doc.get("queryPlanner", {}).get("winningPlan", {})
    if _plan_has_collscan(winning_plan):
        raise ValueError(
            "Consulta rechazada: no se está usando índice (COLLSCAN detectado)."
        )


def set_index_enforcement(enabled: bool) -> bool:
    global INDEX_ENFORCEMENT_ENABLED
    INDEX_ENFORCEMENT_ENABLED = bool(enabled)
    return INDEX_ENFORCEMENT_ENABLED


def get_index_enforcement() -> bool:
    return INDEX_ENFORCEMENT_ENABLED
