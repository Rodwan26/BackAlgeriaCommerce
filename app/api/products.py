from fastapi import APIRouter
from sqlalchemy.orm import Session, joinedload
from app.db.database import SessionLocal
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductResponse
from fastapi import APIRouter, HTTPException
router = APIRouter()


@router.get(
    "/products",
    response_model=list[ProductResponse],
)
def list_products():
    db: Session = SessionLocal()

    try:
        products = (
            db.query(Product)
            .options(joinedload(Product.category))
            .order_by(Product.id.desc())
            .all()
        )

        return products

    finally:
        db.close()


@router.post(
    "/products",
    response_model=ProductResponse,
)
def create_product(product: ProductCreate):
    db: Session = SessionLocal()

    try:
        new_product = Product(
            name=product.name,
            description=product.description,
            price=product.price,
            image=product.image,
            category_id=product.category_id,
        )

        db.add(new_product)
        db.commit()
        db.refresh(new_product)

        # Load the category before closing the session
        if new_product.category_id is not None:
            new_product = (
                db.query(Product)
                .options(joinedload(Product.category))
                .filter(Product.id == new_product.id)
                .first()
            )

        return new_product

    finally:
        db.close()



@router.delete("/products/{product_id}")
def delete_product(product_id: int):
    db: Session = SessionLocal()

    try:
        product = (
            db.query(Product)
            .filter(Product.id == product_id)
            .first()
        )

        if not product:
            return {"message": "Product not found"}

        db.delete(product)
        db.commit()

        return {"message": "Product deleted"}

    finally:
        db.close()

@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int):
    db: Session = SessionLocal()

    try:
        product = (
            db.query(Product)
            .options(joinedload(Product.category))
            .filter(Product.id == product_id)
            .first()
        )

        if not product:
            return {"message": "Product not found"}

        return product

    finally:
        db.close()


@router.put(
    "/products/{product_id}",
    response_model=ProductResponse,
)
def update_product(
    product_id: int,
    data: ProductCreate,
):
    db: Session = SessionLocal()

    try:
        product = (
            db.query(Product)
            .filter(Product.id == product_id)
            .first()
        )

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found",
            )

        product.name = data.name
        product.description = data.description
        product.price = data.price
        product.image = data.image
        product.category_id = data.category_id

        db.commit()
        db.refresh(product)

        # Reload product with category
        product = (
            db.query(Product)
            .options(joinedload(Product.category))
            .filter(Product.id == product_id)
            .first()
        )

        return product

    finally:
        db.close()

 