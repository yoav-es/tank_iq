# app/server.py
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.api as api_module
from app.database import init_db

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown events."""
    logger.info("Application starting up...")
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialization complete.")

    yield

    logger.info("Application shutting down.")


# --- FastAPI App Initialization ---
app = FastAPI(
    title="TankIQ Fuel Tracker API",
    description="API for tracking vehicle fuel consumption "
                "and calculating statistics.",
    version="1.0.0",
    lifespan=lifespan,
)

# --- CORS Middleware ---
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include Router ---
app.include_router(api_module.router)