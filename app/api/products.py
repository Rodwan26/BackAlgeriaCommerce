from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.db.database import SessionLocal
from app.models.product import Product
from app.models.product_option import ProductOption
from app.models.product_variant import ProductVariant
from app.models.product_tag import ProductTag
from app.models.collection import Collection
from app.schemas.product import ProductCreate, ProductResponse

router = APIRouter()


def _load_product(db: Session, product_id: int) -> Product | None:
    return (
        db.query(Product)
        .options(
            joinedload(Product.category),
            joinedload(Product.options),
            joinedload(Product.variants),
            joinedload(Product.tags),
            joinedload(Product.collections),
        )
        .filter(Product.id == product_id)
        .first()
    )


def _validate_collections(db: Session, collection_ids: list[int]) -> list[Collection]:
    if not collection_ids:
        return []

    unique_ids = list(dict.fromkeys(collection_ids))
    found = (
        db.query(Collection)
        .filter(Collection.id.in_(unique_ids))
        .all()
    )
    found_ids = {c.id for c in found}

    missing = [i for i in unique_ids if i not in found_ids]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Collection not found: {missing}",
        )

    return found


@router.get(
    "/products",
    response_model=list[ProductResponse],
)
def list_products():
    db: Session = SessionLocal()

    try:
        products = (
            db.query(Product)
            .options(
                joinedload(Product.category),
                joinedload(Product.options),
                joinedload(Product.variants),
                joinedload(Product.tags),
                joinedload(Product.collections),
            )
            .order_by(Product.id.desc())
            .all()
        )

        return [
            ProductResponse.model_validate(p)
            for p in products
        ]

    finally:
        db.close()


@router.post(
    "/products",
    response_model=ProductResponse,
)
def create_product(product: ProductCreate):
    db: Session = SessionLocal()

    try:
        collections = _validate_collections(
            db,
            product.collections,
        )

        new_product = Product(
            name=product.name,
            description=product.description,
            price=product.price,
            stock=product.stock,
            image=product.image,
            category_id=product.category_id,
            status=product.status,
        )

        for option in product.options:
            new_product.options.append(
                ProductOption(
                    name=option.name,
                    values=option.values,
                )
            )

        for variant in product.variants:
            new_product.variants.append(
                ProductVariant(
                    sku=variant.sku,
                    price=variant.price,
                    stock=variant.stock,
                    image=variant.image,
                    options=variant.options,
                )
            )

        for tag in product.tags:
            new_product.tags.append(
                ProductTag(name=tag)
            )

        new_product.collections = collections

        db.add(new_product)
        db.commit()
        db.refresh(new_product)

        result = _load_product(db, new_product.id)
        return ProductResponse.model_validate(result)

    finally:
        db.close()


@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int):
    db: Session = SessionLocal()

    try:
        product = _load_product(db, product_id)

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found",
            )

        return ProductResponse.model_validate(product)

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
        product = _load_product(db, product_id)

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found",
            )

        collections = _validate_collections(
            db,
            data.collections,
        )

        product.name = data.name
        product.description = data.description
        product.price = data.price
        product.stock = data.stock
        product.image = data.image
        product.category_id = data.category_id
        product.status = data.status

        product.options.clear()
        for option in data.options:
            product.options.append(
                ProductOption(
                    name=option.name,
                    values=option.values,
                )
            )

        product.variants.clear()
        for variant in data.variants:
            product.variants.append(
                ProductVariant(
                    sku=variant.sku,
                    price=variant.price,
                    stock=variant.stock,
                    image=variant.image,
                    options=variant.options,
                )
            )

        product.tags.clear()
        for tag in data.tags:
            product.tags.append(
                ProductTag(name=tag)
            )

        product.collections = collections

        db.commit()
        db.refresh(product)

        result = _load_product(db, product_id)
        return ProductResponse.model_validate(result)

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
