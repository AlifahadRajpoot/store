from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

app=FastAPI()

@app.middleware('http')
async def auth_middleware(request: Request, call_next):
    if request.url.path not in ["/login", "/register","/docs", "/openapi.json", "/redoc","/favicon.ico"]:
        token = request.headers.get("Authorization")
        if not token:
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
        response = await call_next(request)
        return response

@app.middleware('http')
async def logging_middleware(request: Request, call_next):
    print(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    print(f"Response Status: {response.status_code}")
    return response






