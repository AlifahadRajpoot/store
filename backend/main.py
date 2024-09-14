from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from backend.middleware import auth_middleware,logging_middleware
load_dotenv()
from .routers import order_router,payment_router,product_router,user_router,admin_router
from .config.db import create_tables

app=FastAPI()

app.add_middleware(BaseHTTPMiddleware, dispatch=auth_middleware)
app.add_middleware(BaseHTTPMiddleware, dispatch=logging_middleware)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run on startup
    print("App is starting up...")
    
    create_tables()
    yield
    
    # Code to run on shutdown
    print("App is shutting down...")


app=FastAPI(lifespan=lifespan)


app.include_router(user_router.router,tags=["Users"])
app.include_router(order_router.router,tags=["Orders"])
app.include_router(product_router.router,tags=["Product"])
app.include_router(payment_router.router,tags=["Payments"])
app.include_router(admin_router.router,tags=["Admin and Super_Admin"])



def start():
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8080,reload=True)

    
