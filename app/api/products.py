from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session, joinedload
from uuid import uuid4

from app.db.database import SessionLocal
from app.models.product import Product
from app.models.product_option import ProductOption
from app.models.product_variant import ProductVariant
from app.models.product_tag import ProductTag
from app.models.collection import Collection
from app.schemas.product import (
    ProductCreate,
    ProductResponse,
    ProductStatusUpdate,
)

router = APIRouter()


def _generate_unique_sku(db: Session) -> str:
    """
    Generate a unique SKU for a new Variant.

    The Backend is the single source of truth for SKU generation.
    """
    while True:
        sku = f"SKU-{uuid4().hex[:6].upper()}"

        exists = (
            db.query(ProductVariant)
            .filter(ProductVariant.sku == sku)
            .first()
        )

        if not exists:
            return sku


def _load_product(
    db: Session,
    product_id: int,
) -> Product | None:
    """
    Load a product together with all relationships required
    by ProductResponse.
    """
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


def _validate_collections(
    db: Session,
    collection_ids: list[int],
) -> list[Collection]:
    """
    Validate that all requested collection IDs exist.

    Duplicate collection IDs are removed while preserving order.
    """
    if not collection_ids:
        return []

    unique_ids = list(dict.fromkeys(collection_ids))

    found = (
        db.query(Collection)
        .filter(Collection.id.in_(unique_ids))
        .all()
    )

    found_ids = {collection.id for collection in found}

    missing = [
        collection_id
        for collection_id in unique_ids
        if collection_id not in found_ids
    ]

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
            ProductResponse.model_validate(product)
            for product in products
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

        # Create product options.
        for option in product.options:
            new_product.options.append(
                ProductOption(
                    name=option.name,
                    values=option.values,
                )
            )

        # Create product variants.
        #
        # IMPORTANT:
        # The Backend always generates the SKU.
        # Any SKU supplied by the frontend is intentionally ignored.
        for variant in product.variants:
            new_product.variants.append(
                ProductVariant(
                    sku=_generate_unique_sku(db),
                    price=variant.price,
                    stock=variant.stock,
                    image=variant.image,
                    options=variant.options,
                )
            )

        # Create product tags.
        for tag in product.tags:
            new_product.tags.append(
                ProductTag(name=tag)
            )

        new_product.collections = collections

        db.add(new_product)
        db.commit()
        db.refresh(new_product)

        result = _load_product(
            db,
            new_product.id,
        )

        return ProductResponse.model_validate(result)

    finally:
        db.close()


@router.get(
    "/products/{product_id}",
    response_model=ProductResponse,
)
def get_product(product_id: int):
    db: Session = SessionLocal()

    try:
        product = _load_product(
            db,
            product_id,
        )

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found",
            )

        return ProductResponse.model_validate(product)

    finally:
        db.close()


@router.patch(
    "/products/{product_id}/status",
    response_model=ProductResponse,
)
def update_product_status(
    product_id: int,
    data: ProductStatusUpdate,
):
    db: Session = SessionLocal()

    try:
        product = _load_product(
            db,
            product_id,
        )

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found",
            )

        # Only update the product status.
        # Variants, options, tags, collections and SKU are untouched.
        product.status = data.status

        db.commit()
        db.refresh(product)

        result = _load_product(
            db,
            product_id,
        )

        return ProductResponse.model_validate(result)

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
        product = _load_product(
            db,
            product_id,
        )

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found",
            )

        collections = _validate_collections(
            db,
            data.collections,
        )

        # ---------------------------------------------------------
        # Update basic product information.
        # ---------------------------------------------------------

        product.name = data.name
        product.description = data.description
        product.price = data.price
        product.stock = data.stock
        product.image = data.image
        product.category_id = data.category_id
        product.status = data.status

        # ---------------------------------------------------------
        # Replace product options.
        # ---------------------------------------------------------

        product.options.clear()

        for option in data.options:
            product.options.append(
                ProductOption(
                    name=option.name,
                    values=option.values,
                )
            )

        # ---------------------------------------------------------
        # VARIANT MANAGEMENT
        #
        # Important rules:
        #
        # 1. Existing Variant:
        #    - identified by DB id
        #    - keep same id
        #    - keep same SKU
        #    - update price/stock/image/options
        #
        # 2. New Variant:
        #    - id is None
        #    - Backend generates a new SKU
        #
        # 3. Removed Variant:
        #    - delete only that Variant
        #
        # 4. Variant belonging to another product:
        #    - reject with HTTP 400
        #
        # 5. No clear + rebuild.
        # ---------------------------------------------------------

        existing_variants_by_id = {
            variant.id: variant
            for variant in product.variants
        }

        requested_ids: set[int] = set()

        # ---------------------------------------------------------
        # Validate all existing Variant IDs first.
        # ---------------------------------------------------------

        for variant in data.variants:
            if variant.id is None:
                continue

            if variant.id not in existing_variants_by_id:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Variant id {variant.id} does not "
                        "belong to this product."
                    ),
                )

            # Prevent the same DB Variant from being referenced
            # more than once in the same request.
            if variant.id in requested_ids:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Variant id {variant.id} "
                        "was provided more than once."
                    ),
                )

            requested_ids.add(variant.id)

        # ---------------------------------------------------------
        # Delete Variants that existed in DB but were removed
        # from the submitted product.
        # ---------------------------------------------------------

        to_delete = [
            existing
            for existing in product.variants
            if existing.id not in requested_ids
        ]

        for existing in to_delete:
            product.variants.remove(existing)
            db.delete(existing)

        db.flush()

        # ---------------------------------------------------------
        # Update existing Variants in place.
        #
        # Their DB id and SKU remain unchanged.
        # ---------------------------------------------------------

        for variant in data.variants:
            if variant.id is not None:
                existing = existing_variants_by_id[variant.id]

                existing.price = variant.price
                existing.stock = variant.stock
                existing.image = variant.image
                existing.options = variant.options

        # ---------------------------------------------------------
        # Create new Variants.
        #
        # A new Variant is identified by id=None.
        # SKU is ALWAYS generated by the Backend.
        #
        # We intentionally ignore variant.sku from the request.
        # ---------------------------------------------------------

        for variant in data.variants:
            if variant.id is None:
                product.variants.append(
                    ProductVariant(
                        sku=_generate_unique_sku(db),
                        price=variant.price,
                        stock=variant.stock,
                        image=variant.image,
                        options=variant.options,
                    )
                )

        # ---------------------------------------------------------
        # Replace product tags.
        # ---------------------------------------------------------

        product.tags.clear()

        for tag in data.tags:
            product.tags.append(
                ProductTag(name=tag)
            )

        # ---------------------------------------------------------
        # Update collections.
        # ---------------------------------------------------------

        product.collections = collections

        db.commit()
        db.refresh(product)

        result = _load_product(
            db,
            product_id,
        )

        return ProductResponse.model_validate(result)

    finally:
        db.close()


@router.delete(
    "/products/{product_id}",
)
def delete_product(product_id: int):
    db: Session = SessionLocal()

    try:
        product = (
            db.query(Product)
            .filter(Product.id == product_id)
            .first()
        )

        if not product:
            return {
                "message": "Product not found"
            }

        db.delete(product)
        db.commit()

        return {
            "message": "Product deleted"
        }

    finally:
        db.close()