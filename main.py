from fastapi import FastAPI
from  core.settings import settings
from db.base import Base
from db.session import engine

# =====================================================
# Application Bootstrap
# Configures the FastAPI app and registers all routers.
# =====================================================

# Import all the models so that they are registered with SQLAlchemy
from apps.auth import models as auth_models
#Import all roters 
from apps.auth.routers import router as auth_routers
from apps.organization.routers import router as organization_router
from apps.employees.routers import router as em_router
from apps.requests.routers import router as requests_router



app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

#inclouding 
app.include_router(auth_routers)
app.include_router(organization_router)
app.include_router(em_router)
app.include_router(requests_router)
# Avoid schema sync on every boot unless explicitly enabled.
@app.on_event("startup")
def on_startup():
    """Create database tables during startup when the setting is enabled."""
    if settings.CREATE_TABLES_ON_STARTUP:
        Base.metadata.create_all(bind=engine)

# Define a simple root endpoint
@app.get("/")
def read_root():
    """Expose a lightweight entry endpoint for the API."""
    return {"message": f"Welcome to the {settings.APP_NAME} API!"}
