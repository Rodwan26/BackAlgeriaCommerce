from fastapi import APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.database import SessionLocal
from app.models.order import Order
from app.models.product import Product

router = APIRouter()


@router.get("/dashboard/stats")
def dashboard_stats():
    db: Session = SessionLocal()

    try:
        total_sales = (
            db.query(func.coalesce(func.sum(Order.total), 0))
            .filter(Order.status != "cancelled")
            .scalar()
        )

        total_orders = db.query(Order).count()

        pending_orders = (
            db.query(Order)
            .filter(Order.status == "pending")
            .count()
        )

        total_products = db.query(Product).count()

        return {
            "total_sales": total_sales,
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "total_products": total_products,
        }

    finally:
        db.close()