from fastapi import APIRouter
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.product import Product
from app.schemas.product import ProductCreate

router = APIRouter()

@router.get("/products")
def list_products():

    db: Session = SessionLocal()

    products = db.query(Product).order_by(Product.id.desc()).all()

    db.close()

    return products


@router.post("/products")
def create_product(product: ProductCreate):

    db: Session = SessionLocal()

    new_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        image=product.image,
    )

    db.add(new_product)

    db.commit()

    db.refresh(new_product)

    db.close()

    return new_product


@router.delete("/products/{product_id}")
def delete_product(product_id: int):

    db: Session = SessionLocal()

    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        db.close()
        return {"message": "Product not found"}

    db.delete(product)
    db.commit()
    db.close()

    return {"message": "Product deleted"}


@router.put("/products/{product_id}")
def update_product(product_id: int, data: ProductCreate):

    db: Session = SessionLocal()

    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        db.close()
        return {"message": "Product not found"}

    product.name = data.name
    product.description = data.description
    product.price = data.price
    product.image = data.image

    db.commit()
    db.refresh(product)
    db.close()

    return product    