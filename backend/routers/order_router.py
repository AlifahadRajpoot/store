from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from backend.models.schema import UpdateOrder
from backend.models.tables import Order, User
from backend.config.db import engine
from backend.security import get_current_active_user

router=APIRouter()

@router.post("/order")
async def create_order(order:Order):
    with Session(engine) as session:
        session.add(order)
        session.commit()
        session.refresh(order)
        return {"status":200,"Message":"Order created successfully"}
    
@router.get("/order")
async def  get_order():
    with Session(engine) as session:
        orders=session.exec(select(Order)).all()
        return {"status":200,"Message":"Orders retrieved successfully","data":orders}
    
@router.get("/order/{order_id}")
async def get_order_by_id(order_id:int):
    with Session(engine) as session:
        orders=session.exec(select(Order).where(Order.id==order_id)).first()
        if not orders:
            raise HTTPException(status_code=404,detail="Order not found")
        return  {"status":200,"Message":"Order retrieved successfully","data":orders}
    
@router.put("/order/{order_id}/status")
async def update_order_status(order_id:int,orders:UpdateOrder,current_user: User = Depends(get_current_active_user)):
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions to Update status")

    with Session(engine) as session:
        db_order=session.exec(select(Order).where(Order.id==order_id)).first()
        if not db_order:
            raise  HTTPException(status_code=404,detail="Order not found")
        order_data=orders.model_dump(exclude_unset=True)
        db_order.sqlmodel_update(order_data)
        session.add(db_order)
        session.commit()
        session.refresh(db_order)
        return  {"status":200,"Message":"Order status updated successfully","data":db_order}
    



        








        

