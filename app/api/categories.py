from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.category import Category
from app.models.product import Product
from app.schemas.category import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
)

router = APIRouter()


@router.get(
    "/categories",
    response_model=list[CategoryResponse],
)
def list_categories():
    db: Session = SessionLocal()

    try:
        categories = (
            db.query(Category)
            .order_by(Category.name)
            .all()
        )

        return categories

    finally:
        db.close()


@router.get(
    "/categories/{category_id}",
    response_model=CategoryResponse,
)
def get_category(category_id: int):
    db: Session = SessionLocal()

    try:
        category = (
            db.query(Category)
            .filter(Category.id == category_id)
            .first()
        )

        if not category:
            raise HTTPException(
                status_code=404,
                detail="Category not found",
            )

        return category

    finally:
        db.close()


@router.post(
    "/categories",
    response_model=CategoryResponse,
)
def create_category(data: CategoryCreate):
    db: Session = SessionLocal()

    try:
        category = Category(
            name=data.name
        )

        db.add(category)
        db.commit()
        db.refresh(category)

        return category

    finally:
        db.close()


@router.put(
    "/categories/{category_id}",
    response_model=CategoryResponse,
)
def update_category(
    category_id: int,
    data: CategoryUpdate,
):
    db: Session = SessionLocal()

    try:
        category = (
            db.query(Category)
            .filter(Category.id == category_id)
            .first()
        )

        if not category:
            raise HTTPException(
                status_code=404,
                detail="Category not found",
            )

        category.name = data.name

        db.commit()
        db.refresh(category)

        return category

    finally:
        db.close()


@router.delete("/categories/{category_id}")
def delete_category(category_id: int):
    db: Session = SessionLocal()

    try:
        category = (
            db.query(Category)
            .filter(Category.id == category_id)
            .first()
        )

        if not category:
            raise HTTPException(
                status_code=404,
                detail="Category not found",
            )

        products_count = (
            db.query(Product)
            .filter(Product.category_id == category_id)
            .count()
        )

        if products_count > 0:
            raise HTTPException(
                status_code=409,
                detail=(
                    f"Cannot delete category '{category.name}'. "
                    f"It is used by {products_count} product(s)."
                ),
            )

        db.delete(category)
        db.commit()

        return {
            "message": "Category deleted successfully"
        }

    finally:
        db.close()

