# app/server.py

from fastapi import FastAPI
from app.api import router
from app.database import init_db
from contextlib import asynccontextmanager # 🛑 NEW IMPORT

# Define the modern lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown events."""
    # --- STARTUP EVENT (Runs before the app starts serving) ---
    print("Initializing database...")
    init_db() 
    print("Database initialization complete.")
    
    # Yield control to the application
    yield 
    
    # --- SHUTDOWN EVENT (Runs when the app shuts down) ---
    # Any necessary cleanup goes here (e.g., closing a connection pool)
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