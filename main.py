from fastapi import FastAPI

from core.settings import settings

# =====================================================
# Application Bootstrap
# Configures the FastAPI app and registers all routers.
# =====================================================

# Import all routers.
from apps.auth.routers import router as auth_routers
from apps.organization.routers import router as organization_router
from apps.employees.routers import router as em_router
from apps.requests.routers import router as requests_router



app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

# Include application routers.
app.include_router(auth_routers)
app.include_router(organization_router)
app.include_router(em_router)
app.include_router(requests_router)

# Define a simple root endpoint
@app.get("/")
def read_root():
    """Expose a lightweight entry endpoint for the API."""
    return {"message": f"Welcome to the {settings.APP_NAME} API!"}
