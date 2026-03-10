import sys
from pathlib import Path

from pymongo.errors import OperationFailure

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from crud.common import get_db, load_dotenv_file


# In self-hosted MongoDB deployments, notablescan can force index-only query plans.
# In MongoDB Atlas this parameter is usually restricted; this script reports that clearly.
def main() -> None:
    load_dotenv_file()
    db = get_db()

    try:
        db.command({"setParameter": 1, "notablescan": True})
        print("notablescan activado: consultas sin indice seran rechazadas por el servidor.")
    except OperationFailure as exc:
        print("No se pudo activar notablescan en este entorno (comun en MongoDB Atlas).")
        print(f"Detalle: {exc}")
        print("Alternativa recomendada: validar consultas con explain() y usar hint() en rutas criticas.")


if __name__ == "__main__":
    main()
