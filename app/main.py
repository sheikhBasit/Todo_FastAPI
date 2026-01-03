from importlib import import_module
from fastapi import FastAPI
from .config.database import engine, Base
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.middleware.logging_middleware import LoggingMiddleware
from app.middleware.authentication_middleware import AuthenticationMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import logging
import os

# Create tables if they don't exist - usually handled by migrations
# Base.metadata.create_all(bind=engine)

app = FastAPI(title="ToDo API")


# Initialize the Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "https://your-production-domain.com"],  # Restrict origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("middleware")

# Add middlewares to the app
if os.getenv("ENV", "development") != "production":
    app.add_middleware(LoggingMiddleware)
app.add_middleware(AuthenticationMiddleware)

# Add GZip middleware
app.add_middleware(GZipMiddleware, minimum_size=10000)

# Dynamically include routers
ROUTER_MODULES = ["auth", "groups", "tasks", "health"]
for module_name in ROUTER_MODULES:
    module = import_module(f".routers.{module_name}", package="app")
    app.include_router(module.router)

@limiter.limit("5/minute")
@app.get("/")
def root():
    return {"message": "API is online. Go to /docs for Swagger UI"}