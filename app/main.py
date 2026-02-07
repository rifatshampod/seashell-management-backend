from fastapi import FastAPI
from app.core.config import get_settings
from app.api.v1 import auth

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Seashell Management Backend API",
)

# Include routers
app.include_router(auth.router)


@app.get("/")
def read_root():
    """Root endpoint."""
    return {"message": "Seashell Management Backend API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
