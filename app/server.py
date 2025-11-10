# app/server.py
import logging
from fastapi import FastAPI
from app.api import router
from app.database import init_db
from contextlib import asynccontextmanager # 🛑 NEW IMPORT

# --- 🛑 LOGGING CONFIGURATION (Runs first) ---
# Set the global logging level and format.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
# Get the logger instance for the server module
logger = logging.getLogger(__name__) 

# Define the modern lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown events."""
    # --- STARTUP EVENT (Runs before the app starts serving) ---
    logger.info("Application starting up...") # 🛑 LOGGING
    logger.info("Initializing database...")
    init_db() 
    logger.info("Database initialization complete.")
    
    # Yield control to the application
    yield 
    
    # --- SHUTDOWN EVENT (Runs when the app shuts down) ---
    # Any necessary cleanup goes here (e.g., closing a connection pool)
    logger.info("Application shutting down.") # 🛑 LOGGING
    pass


# Initialize the FastAPI app instance, passing the lifespan handler
app = FastAPI(
    title="TankIQ Fuel Tracker API",
    description="API for tracking vehicle fuel consumption and calculating statistics.",
    version="1.0.0",
    lifespan=lifespan  # 🛑 PASS THE HANDLER
)

# Include the Router
app.include_router(router)