from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.routes import auth, me, users, groups, admin, permissions, health

app = FastAPI(title="TenantCore IAM Canonical Example")

app.include_router(auth.router)
app.include_router(me.router)
app.include_router(users.router)
app.include_router(groups.router)
app.include_router(admin.router)
app.include_router(permissions.router)
app.include_router(health.router)

@app.exception_handler(Exception)
def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )
