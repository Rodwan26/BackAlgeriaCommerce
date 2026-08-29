from fastapi import FastAPI
from app.api.orders import router as orders_router
from app.db.database import Base, engine
import app.models.product
from app.api.products import router as products_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.upload import router as upload_router
from app.api.categories import router as categories_router
import app.models.product
import app.models.category
import app.models.order
import app.models.carrier
import app.models.carrier_connection
from app.api.dashboard import router as dashboard_router
from app.api.customers import router as customers_router
from app.api.shipping import router as shipping_router

app = FastAPI(title="E-Commerce API")
app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads",
)
Base.metadata.create_all(bind=engine)



app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://front-algeria-commerce.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(customers_router)
app.include_router(dashboard_router)
app.include_router(products_router)
app.include_router(upload_router)
app.include_router(categories_router)
app.include_router(orders_router)
app.include_router(shipping_router)

@app.get("/")
def root():
    return {
        "message": "Backend Running"
    }