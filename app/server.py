# app/server.py
"""
TankIQ Server Module

This module initializes the FastAPI application, configures logging,
sets up middleware, and manages application lifespan events.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.api as api_module
from app.database import init_db

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle application startup and shutdown events.

    On startup:
        - Initialize the database schema.
    On shutdown:
        - Log application termination.
    """
    logger.info("Application starting up...")
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialization complete.")

    yield

    logger.info("Application shutting down.")


# FastAPI application initialization
app = FastAPI(
    title="TankIQ Fuel Tracker API",
    description="API for tracking vehicle fuel consumption and calculating statistics.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware configuration
# Note: Origins are set to '*' for development. Restrict in production.
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_module.router)
