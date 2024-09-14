from typing import List, Optional
from sqlmodel import SQLModel,Field,Relationship
from datetime import datetime

class User(SQLModel,table=True):
    id: int = Field(default=None,primary_key=True)
    username:str
    email: str
    hashed_password:str
    role:str
    
    orders:List['Order']=Relationship(back_populates="user")
    payments:List['Payment']=Relationship(back_populates="user")
    
class OrderItem(SQLModel,table=True):
    id: int = Field(default=None,primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    order_id: int = Field(foreign_key="order.id")
    quantity: int
    orders:'Order'=Relationship(back_populates="items")
    product:'Product'=Relationship(back_populates="items")
    
class Product(SQLModel,table=True):
    id:int=Field(default=None,primary_key=True)
    name:str
    description:str
    price:float
    stock:int
    orders:List['Order']=Relationship(back_populates="products",link_model=OrderItem)
    items:List[OrderItem]=Relationship(back_populates="product")
    
class Order(SQLModel,table=True):
    id: int = Field(default=None,primary_key=True)
    user_id:int=Field(default=None,foreign_key="user.id")
    status:str
    order_date:datetime=Field(default_factory=datetime.now)
    delivery_date:Optional[datetime]=None
    user:User=Relationship(back_populates="orders")
    products:List[Product]=Relationship(back_populates="orders",link_model=OrderItem)
    payments:'Payment'=Relationship(back_populates="orders")
    items:List[OrderItem]=Relationship(back_populates="orders")
    
class Payment(SQLModel,table=True):
    id:Optional[int]=Field(default=None,primary_key=True)
    user_id:Optional[int]=Field(default=None,foreign_key="user.id")
    order_id:Optional[int]=Field(default=None,foreign_key="order.id")
    amount:float
    currency:str
    payment_status:str
    payment_method:str
    payment_date:datetime=Field(default_factory=datetime.now)
    stripe_payment_intent_id: str
    user:User=Relationship(back_populates="payments")
    orders:Order=Relationship(back_populates="payments")
    
    

    


