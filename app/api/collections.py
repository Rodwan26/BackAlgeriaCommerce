from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.collection import Collection
from app.models.product_collection import product_collections
from app.schemas.collection import (
    CollectionCreate,
    CollectionResponse,
    CollectionUpdate,
)

router = APIRouter()


@router.get(
    "/collections",
    response_model=list[CollectionResponse],
)
def list_collections():
    db: Session = SessionLocal()

    try:
        collections = (
            db.query(Collection)
            .order_by(Collection.name)
            .all()
        )

        return collections

    finally:
        db.close()


@router.get(
    "/collections/{collection_id}",
    response_model=CollectionResponse,
)
def get_collection(collection_id: int):
    db: Session = SessionLocal()

    try:
        collection = (
            db.query(Collection)
            .filter(Collection.id == collection_id)
            .first()
        )

        if not collection:
            raise HTTPException(
                status_code=404,
                detail="Collection not found",
            )

        return collection

    finally:
        db.close()


@router.post(
    "/collections",
    response_model=CollectionResponse,
)
def create_collection(data: CollectionCreate):
    db: Session = SessionLocal()

    try:
        collection = Collection(
            name=data.name
        )

        db.add(collection)
        db.commit()
        db.refresh(collection)

        return collection

    finally:
        db.close()


@router.put(
    "/collections/{collection_id}",
    response_model=CollectionResponse,
)
def update_collection(
    collection_id: int,
    data: CollectionUpdate,
):
    db: Session = SessionLocal()

    try:
        collection = (
            db.query(Collection)
            .filter(Collection.id == collection_id)
            .first()
        )

        if not collection:
            raise HTTPException(
                status_code=404,
                detail="Collection not found",
            )

        collection.name = data.name

        db.commit()
        db.refresh(collection)

        return collection

    finally:
        db.close()


@router.delete("/collections/{collection_id}")
def delete_collection(collection_id: int):
    db: Session = SessionLocal()

    try:
        collection = (
            db.query(Collection)
            .filter(Collection.id == collection_id)
            .first()
        )

        if not collection:
            raise HTTPException(
                status_code=404,
                detail="Collection not found",
            )

        products_count = (
            db.query(product_collections.c.product_id)
            .filter(
                product_collections.c.collection_id
                == collection_id
            )
            .count()
        )

        if products_count > 0:
            raise HTTPException(
                status_code=409,
                detail=(
                    f"Cannot delete collection '{collection.name}'. "
                    f"It is linked to {products_count} product(s)."
                ),
            )

        db.delete(collection)
        db.commit()

        return {
            "message": "Collection deleted successfully"
        }

    finally:
        db.close()
