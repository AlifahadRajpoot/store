from sqlmodel import SQLModel

class UpdateUser(SQLModel):
    username:str
    email:str
    hash_password:str
    role:str
    
class UserRoleUpdate(SQLModel):
    role:str
    
class UpdateProduct(SQLModel):
    name:str
    description:str
    price:float
    stock:int

class UpdateOrder(SQLModel):
    status:str
    

class CreateAdminRequest(SQLModel):
    id:int
    username: str
    email:str
    hashed_password:str
    role: str
    