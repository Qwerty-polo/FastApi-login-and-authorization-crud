from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy import select
from Routers.simple_ws import manager
from database import get_db
from models import UserModel, DishModel, OrderModel, OrderItemModel
from schemas import OrderCreate, OrderResponse
from Routers.login import SessionDep, UserDep, security_headers
from sqlalchemy.orm import selectinload

router = APIRouter()

@router.post('/orders', response_model=OrderResponse,dependencies=[Depends(security_headers)])
async def create_order(
        order_data: OrderCreate,
        db: SessionDep,
        user: UserDep
    ):
    current_user_id = int(user.sub)
    new_order = OrderModel(
        user_id=current_user_id,
        total_price=0.0
    )

    db.add(new_order)
    await db.flush()

    for item in order_data.items:

        dish = select(DishModel).where(DishModel.id==item.dish_id)
        rezult = await db.execute(dish)

        dish_db = rezult.scalar_one_or_none()

        if dish_db is None:
            raise HTTPException(status_code=404, detail="Item not found")

        new_order_item = OrderItemModel(
            order_id=new_order.id,
            dish_id=dish_db.id,
            quantity=item.quantity,
            price=dish_db.price
        )
        new_order.total_price += dish_db.price * item.quantity

        db.add(new_order_item)

    await db.commit()

    query = (
        select(OrderModel)
        .options(selectinload(OrderModel.items))  # <--- Ключовий момент! "Завантаж items одразу"
        .where(OrderModel.id == new_order.id)
    )

    result = await db.execute(query)

    full_order = result.scalar_one()

    message = f"Нове замовлення #{full_order.id}! Сума: {full_order.total_price} грн"

    await manager.broadcast(message)

    return full_order