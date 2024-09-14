from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from backend.models.tables import User, Order
from backend.models.schema import CreateAdminRequest
from backend.security import get_current_active_user,get_password_hash
from backend.config.db import engine

router = APIRouter()


@router.get("/admin/dashboard")
async def admin_dashboard(current_user: User = Depends(get_current_active_user)):
    if current_user.role  != "admin":
        raise HTTPException(status_code=401, detail="Not admin")
    with Session(engine) as session:
        orders = session.exec(select(Order)).all()
        customers = session.exec(select(User).where(User.role == "simple_user")).all()
        return {
            "status": 200,
            "orders": orders,
            "customers": customers
        }

@router.post("/admin/approve/{user_id}")
async def approve_admin_request(user_id: int,current_user: User = Depends(get_current_active_user)):
    if current_user.role  != "super_admin":
        raise  HTTPException(status_code=401, detail="Not super admin")
    with  Session(engine) as session:
        user = session.exec(select(User).where(User.id == user_id)).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.role == "admin":
            raise HTTPException(status_code=400, detail="User is already an admin")
    
        user.role = "admin"
        session.add(user)
        session.commit()
        session.refresh(user)
        
        return {
            "status": 200,
            "message": f"User {user.username} has been approved as an admin.",
            "user": user
        }

@router.delete("/admin/remove/{admin_id}")
async def remove_admin(admin_id: int,current_user: User = Depends(get_current_active_user)):
    if current_user.role  != "super_admin":
        raise  HTTPException(status_code=401, detail="Not super admin")
    with Session(engine) as session:

        admin = session.exec(select(User).where(User.id == admin_id, User.role == "admin")).first()
        
        if not admin:
            raise HTTPException(status_code=404, detail="Admin not found")
        admin.role = "simple_user"
        session.add(admin)
        session.commit()
        session.refresh(admin)
        
        return {
            "status": 200,
            "message": f"Admin {admin.username} has been removed and demoted to a simple user.",
            "user": admin
        }

@router.post("/superadmin/create_admin")
async def create_admin(admin_request:CreateAdminRequest,current_user: User = Depends(get_current_active_user)):
    if  current_user.role  != "super_admin":
        raise  HTTPException(status_code=401, detail="Not super admin")
    with Session(engine) as session:

        existing_user = session.exec(select(User).where(User.email == admin_request.email)).first()
        
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this username already exists")
        
        new_admin = User(
            id=admin_request.id,
            username=admin_request.username,
            email=admin_request.email,
            hashed_password=get_password_hash(admin_request.hashed_password),
            role="admin" 
        )
        session.add(new_admin)
        session.commit()
        session.refresh(new_admin)
        
        return {
            "status": 200,
            "message": f"Admin {new_admin.username} has been created successfully.",
            "user": new_admin
        }
