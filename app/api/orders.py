from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.db.database import SessionLocal
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.schemas.order import OrderCreate, OrderResponse


router = APIRouter()


# =========================================================
# CREATE ORDER
# =========================================================

@router.post(
    "/orders",
    response_model=OrderResponse,
)
def create_order(data: OrderCreate):

    db: Session = SessionLocal()

    try:
        total = 0
        order_items = []

        # Check products and calculate total
        for item in data.items:

            product = (
                db.query(Product)
                .filter(Product.id == item.product_id)
                .first()
            )

            if not product:
                raise HTTPException(
                    status_code=404,
                    detail=f"Product {item.product_id} not found",
                )

            if item.quantity <= 0:
                raise HTTPException(
                    status_code=400,
                    detail="Quantity must be greater than 0",
                )

            item_total = product.price * item.quantity
            total += item_total

            order_items.append(
                OrderItem(
                    product_id=product.id,
                    quantity=item.quantity,
                    price=product.price,
                )
            )

        # Create order
        order = Order(
            customer_name=data.customer_name,
            customer_phone=data.customer_phone,
            customer_address=data.customer_address,
            total=total,
            status="pending",
        )

        db.add(order)
        db.flush()

        # Attach order items
        for item in order_items:
            item.order_id = order.id
            db.add(item)

        db.commit()

        # Reload order with items and products
        order = (
            db.query(Order)
            .options(
                joinedload(Order.items)
                .joinedload(OrderItem.product)
            )
            .filter(Order.id == order.id)
            .first()
        )

        return order

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# =========================================================
# GET ALL ORDERS
# =========================================================

@router.get(
    "/orders",
    response_model=list[OrderResponse],
)
def list_orders():

    db: Session = SessionLocal()

    try:
        orders = (
            db.query(Order)
            .options(
                joinedload(Order.items)
                .joinedload(OrderItem.product)
            )
            .order_by(Order.id.desc())
            .all()
        )

        return orders

    finally:
        db.close()


# =========================================================
# GET SINGLE ORDER
# =========================================================

@router.get(
    "/orders/{order_id}",
    response_model=OrderResponse,
)
def get_order(order_id: int):

    db: Session = SessionLocal()

    try:
        order = (
            db.query(Order)
            .options(
                joinedload(Order.items)
                .joinedload(OrderItem.product)
            )
            .filter(Order.id == order_id)
            .first()
        )

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found",
            )

        return order

    finally:
        db.close()


# =========================================================
# UPDATE ORDER STATUS
# =========================================================

@router.put("/orders/{order_id}/status")
def update_order_status(
    order_id: int,
    status: str,
):

    db: Session = SessionLocal()

    try:

        order = (
            db.query(Order)
            .filter(Order.id == order_id)
            .first()
        )

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found",
            )

        allowed_statuses = {
            "pending",
            "confirmed",
            "shipped",
            "delivered",
            "cancelled",
        }

        if status not in allowed_statuses:
            raise HTTPException(
                status_code=400,
                detail="Invalid order status",
            )

        order.status = status

        db.commit()
        db.refresh(order)

        return {
            "message": "Order status updated",
            "status": order.status,
        }

    finally:
        db.close()

