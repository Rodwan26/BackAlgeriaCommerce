from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.db.database import SessionLocal
from app.models.customer import Customer
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

        # -------------------------------------------------
        # Validate delivery type
        # -------------------------------------------------

        allowed_delivery_types = {
            "home",
            "pickup",
        }

        if data.delivery_type not in allowed_delivery_types:
            raise HTTPException(
                status_code=400,
                detail="Invalid delivery type. Use 'home' or 'pickup'.",
            )

        # -------------------------------------------------
        # Validate customer
        # -------------------------------------------------

        customer = (
            db.query(Customer)
            .filter(Customer.id == data.customer_id)
            .first()
        )

        if not customer:
            raise HTTPException(
                status_code=404,
                detail="Customer not found",
            )

        # -------------------------------------------------
        # Validate items
        # -------------------------------------------------

        if not data.items:
            raise HTTPException(
                status_code=400,
                detail="Order must contain at least one item",
            )

        for item in data.items:

            if item.quantity <= 0:
                raise HTTPException(
                    status_code=400,
                    detail="Quantity must be greater than 0",
                )

        # -------------------------------------------------
        # Calculate required quantity per product
        #
        # Protects against the same product appearing
        # multiple times in the same order.
        # -------------------------------------------------

        required_quantities = {}

        for item in data.items:

            required_quantities[item.product_id] = (
                required_quantities.get(item.product_id, 0)
                + item.quantity
            )

        # -------------------------------------------------
        # Lock products in a consistent order
        #
        # FOR UPDATE prevents concurrent transactions
        # from modifying the same product simultaneously.
        # -------------------------------------------------

        products = {}

        for product_id in sorted(required_quantities.keys()):

            product = (
                db.query(Product)
                .filter(Product.id == product_id)
                .with_for_update()
                .first()
            )

            if not product:

                raise HTTPException(
                    status_code=404,
                    detail=f"Product {product_id} not found",
                )

            products[product_id] = product

        # -------------------------------------------------
        # Check stock
        # -------------------------------------------------

        for product_id, required_quantity in required_quantities.items():

            product = products[product_id]

            if required_quantity > product.stock:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Insufficient stock for product "
                        f"{product.id}. "
                        f"Available: {product.stock}, "
                        f"requested: {required_quantity}"
                    ),
                )

        # -------------------------------------------------
        # Calculate total
        # -------------------------------------------------

        total = 0

        order_items = []

        for item in data.items:

            product = products[item.product_id]

            item_total = product.price * item.quantity

            total += item_total

            order_items.append(
                OrderItem(
                    product_id=product.id,
                    quantity=item.quantity,
                    price=product.price,
                )
            )

        # -------------------------------------------------
        # Decrease stock
        # -------------------------------------------------

        for product_id, quantity in required_quantities.items():

            product = products[product_id]

            product.stock -= quantity

        # -------------------------------------------------
        # Create order
        # -------------------------------------------------

        order = Order(
            customer_id=customer.id,
            delivery_type=data.delivery_type,
            total=total,
            status="pending",
        )

        db.add(order)

        db.flush()

        # -------------------------------------------------
        # Attach order items
        # -------------------------------------------------

        for item in order_items:

            item.order_id = order.id

            db.add(item)

        # -------------------------------------------------
        # Commit everything together
        #
        # Order
        # OrderItems
        # Stock changes
        # -------------------------------------------------

        db.commit()

        # -------------------------------------------------
        # Reload complete order
        # -------------------------------------------------

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