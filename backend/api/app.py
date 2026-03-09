from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.restaurants import router as restaurants_router
from api.routes.orders import router as orders_router
from api.routes.reviews import router as reviews_router

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


@app.get("/")
def root():
    return {"message": "MesaLista API funcionando"}