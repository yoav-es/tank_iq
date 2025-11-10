import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# 🛑 CRITICAL FIX: Use an alias to safely import the router module
import app.api as api_module
from app.database import init_db
from contextlib import asynccontextmanager 

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
    logger.info("Application starting up...") 
    logger.info("Initializing database...")
    init_db() 
    logger.info("Database initialization complete.")
    
    # Yield control to the application
    yield 
    
    # --- SHUTDOWN EVENT (Runs when the app shuts down) ---
    logger.info("Application shutting down.") 
    pass


# Initialize the FastAPI app instance, passing the lifespan handler
app = FastAPI(
    title="TankIQ Fuel Tracker API",
    description="API for tracking vehicle fuel consumption and calculating statistics.",
    version="1.0.0",
    lifespan=lifespan 
)

# --- CORS MIDDLEWARE ---
origins = [
    "*", 
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include the Router
# 🛑 CRITICAL FIX: Reference the router via the imported alias
app.include_router(api_module.router)