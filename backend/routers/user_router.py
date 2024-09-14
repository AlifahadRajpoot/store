from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from backend.config.db import  engine
from backend.models.schema import UpdateUser, UserRoleUpdate
from backend.models.tables import User
from backend.security import authenticate_user, create_access_token, get_current_active_user, get_current_user, get_password_hash

router=APIRouter()

@router.post("/user/register")
async def register_user(user: User):
    with Session(engine) as session:
        existing_user = session.exec(select(User).where((User.username == user.username) | (User.email == user.email))).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")
        
        user.hashed_password = get_password_hash(user.hashed_password)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

@router.post("/login", response_model=dict)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    with Session(engine) as session:
        user = authenticate_user(session, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}

@router.get("/user/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/user/me")
async def update_user_profile(userdata: UpdateUser,current_user: User = Depends(get_current_active_user)):
    
    if current_user.role not in ["simple_user", "admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions to update profile")
    with Session(engine) as session:
        statement = select(User).where(User.id == current_user.id)
        db_user = session.exec(statement).first()
        if not db_user:
            raise  HTTPException(status_code=404,detail="User not found")
        user_data=userdata.model_dump(exclude_unset=True)
        db_user.sqlmodel_update(user_data)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return {"status":200,"Message":"User  profile updated successfully"}

@router.get("/user/")
async def list_all_users(current_user: User = Depends(get_current_active_user)):
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions to view users")

    with Session(engine) as session:
        users = session.exec(select(User)).all()
        return {"users": users}
    

@router.put("/user/{user_id}/role")
async def change_user_role(user_id: int,role_update: UserRoleUpdate,current_user: User = Depends(get_current_active_user)):
    if current_user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Not enough permissions to change user roles")
    
    with Session(engine) as session:
        statement = select(User).where(User.id == user_id)
        db_user = session.exec(statement).first()
        
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        db_user.role = role_update.role
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

        return {"message": f"User role updated to {db_user.role}"}