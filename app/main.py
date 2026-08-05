from fastapi import FastAPI

from app.db.database import Base, engine
import app.models.product
from app.api.products import router as products_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="E-Commerce API")

Base.metadata.create_all(bind=engine)



app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(products_router)


@app.get("/")
def root():
    return {
        "message": "Backend Running"
    }