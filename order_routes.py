from fastapi import APIRouter, Depends, HTTPException, status
from schemas import OrderModel
from models import User, Order
from werkzeug.security import generate_password_hash, check_password_hash
from fastapi_jwt_auth import AuthJWT
from fastapi.encoders import jsonable_encoder
from database import Session, engine

order_router = APIRouter(
    prefix="/orders",
    tags=["orders"],
)

session = Session(bind=engine)

@order_router.get("/all")
async def order(Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token [UnAuthorized]")

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()
    if user.is_staff:
        all_orders = session.query(Order).all()
        response = []
        for order in all_orders:
            response.append({
                "order_id": order.id,
                "quantity": order.quantity,
                "order_status": order.order_status.code,
                "pizza_size": order.pizza_size.code,
                "user_id": order.user_id
            })

        return jsonable_encoder(response)
    
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not Superuser")

@order_router.post("/order", status_code=status.HTTP_201_CREATED)
async def create_order(order: OrderModel, Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token [UnAuthorized]")
    
    current_user = Authorize.get_jwt_subject()
    db_user = session.query(User).filter(User.username == current_user).first()
    new_order = Order(
        quantity=order.quantity,
        order_status=order.order_status,
        pizza_size=order.pizza_size,
        user_id=db_user.id
    )
    new_order.users = db_user
    session.add(new_order)
    session.commit()

    response = {
        "order_id": new_order.id,
        "quantity": new_order.quantity,
        "order_status": new_order.order_status.code,
        "pizza_size": new_order.pizza_size.code,
        "user_id": new_order.user_id
    }


    return jsonable_encoder(response)