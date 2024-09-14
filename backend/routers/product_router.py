from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from backend.config.db import  engine
from backend.models.schema import UpdateProduct
from backend.models.tables import Product, User
from backend.security import get_current_active_user

router=APIRouter()

@router.post("/product")
async def create_product(product: Product,current_user:User=Depends(get_current_active_user)):
    if current_user.role not in ["admin","super_admin"]:
        raise HTTPException(status_code=403,detail="You are not authorized to create a product")
    with Session(engine) as session:
        session.add(product)
        session.commit()
        session.refresh(product)
        return {"status":200,"Messsage":"Product Created  Successfully"}
    
@router.get("/product")
async def get_product():
    with Session(engine) as session:
        products = session.exec(select(Product)).all()
        return {"status":200,"Messsage":"Product Retrieved  Successfully", "data":products}
    
@router.get("/product/{product_id}")
async def get_product_by_id(product_id: int):
    with Session(engine) as session:
        products=session.exec(select(Product).where(Product.id==product_id)).first()
        if not products:
            raise  HTTPException(status_code=404, detail="Product not found")
        return  {"status":200,"Messsage":"Product Retrieved  Successfully", "data":products}
    
@router.put("/product/{product_id}")
async def update_product(product_id: int, product: UpdateProduct,current_user:User=Depends(get_current_active_user)):
    if current_user.role not in ["admin","super_admin"]:
        raise HTTPException(status_code=403,detail="You are not authorized to update a product")

    with Session(engine) as session:
        db_product=session.exec(select(Product).where(Product.id==product_id)).first()
        if not db_product:
            raise HTTPException(status_code=404,details="Product not found")
        product_data=product.model_dump(exclude_unset=True)
        db_product.sqlmodel_update(product_data)
        session.add(db_product)
        session.commit()
        session.refresh(db_product)
        return  {"status":200,"Messsage":"Product Updated  Successfully", "data":db_product}
    
@router.delete("/product/{product_id}")
async def delete_product(product_id: int,current_user:User=Depends(get_current_active_user)):
    if current_user.role not in ["admin","super_admin"]:
        raise HTTPException(status_code=403,detail="You are not authorized to delete a product")
    with Session(engine) as session:
        db_product=session.exec(select(Product).where(Product.id==product_id)).first()
        if not db_product:
            raise HTTPException(status_code=404,details="Product not found")
        session.delete(db_product)
        session.commit()
        session.refresh(db_product)
        return   {"status":200,"Messsage":"Product Deleted  Successfully"}
    
        
        











    



