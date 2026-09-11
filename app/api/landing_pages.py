from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.db.database import SessionLocal
from app.models.landing_page import LandingPage
from app.schemas.landing_page import (
    LandingPageCreate,
    LandingPageResponse,
    LandingPageUpdate,
)

router = APIRouter()


def _load(slug: str) -> LandingPage | None:
    db: Session = SessionLocal()

    try:
        return (
            db.query(LandingPage)
            .filter(LandingPage.slug == slug)
            .first()
        )
    finally:
        db.close()


@router.get("/landing-pages", response_model=list[LandingPageResponse])
def list_landing_pages():
    db: Session = SessionLocal()

    try:
        pages = (
            db.query(LandingPage)
            .options(joinedload(LandingPage.product))
            .order_by(LandingPage.id.desc())
            .all()
        )

        return [
            LandingPageResponse.model_validate(p)
            for p in pages
        ]
    finally:
        db.close()


@router.get("/landing-pages/{slug}", response_model=LandingPageResponse)
def get_landing_page(slug: str):
    db: Session = SessionLocal()

    try:
        page = (
            db.query(LandingPage)
            .options(joinedload(LandingPage.product))
            .filter(LandingPage.slug == slug)
            .first()
        )

        if not page:
            raise HTTPException(
                status_code=404,
                detail="Landing page not found",
            )

        return LandingPageResponse.model_validate(page)
    finally:
        db.close()


@router.post("/landing-pages", response_model=LandingPageResponse)
def create_landing_page(data: LandingPageCreate):
    db: Session = SessionLocal()

    try:
        existing_slug = (
            db.query(LandingPage)
            .filter(LandingPage.slug == data.slug)
            .first()
        )

        if existing_slug:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Landing page with slug "
                            f"'{data.slug}' already exists"
                ),
            )

        page = LandingPage(
            product_id=data.product_id,
            slug=data.slug,
            title=data.title,
            brand=data.brand,
            header_colors=data.header_colors,
            sections=data.sections,
        )

        db.add(page)
        db.commit()
        db.refresh(page)

        return LandingPageResponse.model_validate(page)
    finally:
        db.close()


@router.put("/landing-pages/{page_id}", response_model=LandingPageResponse)
def update_landing_page(page_id: int, data: LandingPageUpdate):
    db: Session = SessionLocal()

    try:
        page = (
            db.query(LandingPage)
            .filter(LandingPage.id == page_id)
            .first()
        )

        if not page:
            raise HTTPException(
                status_code=404,
                detail="Landing page not found",
            )

        existing_slug = (
            db.query(LandingPage)
            .filter(
                LandingPage.slug == data.slug,
                LandingPage.id != page_id,
            )
            .first()
        )

        if existing_slug:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Landing page with slug "
                    f"'{data.slug}' already exists"
                ),
            )

        page.product_id = data.product_id
        page.slug = data.slug
        page.title = data.title
        page.brand = data.brand
        page.header_colors = data.header_colors
        page.sections = data.sections

        db.commit()
        db.refresh(page)

        return LandingPageResponse.model_validate(page)
    finally:
        db.close()


@router.delete("/landing-pages/{page_id}")
def delete_landing_page(page_id: int):
    db: Session = SessionLocal()

    try:
        page = (
            db.query(LandingPage)
            .filter(LandingPage.id == page_id)
            .first()
        )

        if not page:
            return {"message": "Landing page not found"}

        db.delete(page)
        db.commit()

        return {"message": "Landing page deleted"}
    finally:
        db.close()
