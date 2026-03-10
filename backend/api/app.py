from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.restaurants import router as restaurants_router
from api.routes.orders import router as orders_router
from api.routes.reviews import router as reviews_router
from api.routes.users import router as users_router
from api.routes.reports import router as reports_router
from api.routes.arrays import router as arrays_router
from api.routes.transactions_routes import router as transactions_router
from api.routes.gridfs_routes import router as gridfs_router
from api.routes.indices import router as indices_router
from api.routes.admin import router as admin_router

app = FastAPI(title="MesaLista API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(restaurants_router)
app.include_router(orders_router)
app.include_router(reviews_router)
app.include_router(users_router)
app.include_router(reports_router)
app.include_router(arrays_router)
app.include_router(transactions_router)
app.include_router(gridfs_router)
app.include_router(indices_router)
app.include_router(admin_router)


@app.get("/")
def root():
    return {"message": "MesaLista API funcionando"}