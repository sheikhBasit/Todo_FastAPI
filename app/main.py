from fastapi import FastAPI
from .config.database import engine, Base
from .routers import auth, groups, tasks, health

# Create tables if they don't exist - usually handled by migrations
# Base.metadata.create_all(bind=engine)

app = FastAPI(title="ToDo API")

# Include Routers
app.include_router(auth.router)
app.include_router(groups.router)
app.include_router(tasks.router)
app.include_router(health.router)

@app.get("/")
def root():
    return {"message": "API is online. Go to /docs for Swagger UI"}