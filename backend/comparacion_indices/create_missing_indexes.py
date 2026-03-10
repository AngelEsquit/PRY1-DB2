import os

from dotenv import load_dotenv
from pymongo import ASCENDING, MongoClient


def main() -> None:
    load_dotenv()

    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise ValueError("MONGO_URI no esta configurada")

    db_name = os.getenv("MONGO_DB_NAME", "restaurantes_db")
    client = MongoClient(mongo_uri)
    db = client[db_name]

    idx_partial = db.ordenes.create_index(
        [("estado", ASCENDING), ("fecha_pedido", ASCENDING)],
        name="idx_ordenes_activas_parcial",
        partialFilterExpression={
            "estado": {
                "$in": [
                    "pendiente",
                    "confirmado",
                    "en_preparacion",
                    "en_camino",
                    "entregado",
                ]
            }
        },
    )

    idx_multikey = db.restaurantes.create_index(
        [("tipo_comida", ASCENDING)],
        name="idx_restaurantes_tipo_comida_multikey",
    )

    print("Indices listos:", idx_partial, idx_multikey)


if __name__ == "__main__":
    main()
