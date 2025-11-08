TankIQ/
├── app/                         # Core application logic
│   ├── __init__.py             # Initializes the app package
│   ├── models.py               # Defines FuelEntry class and data schema
│   ├── database.py             # Handles SQLite connection and setup
│   ├── routes.py               # FastAPI endpoints for CRUD operations
│   ├── utils.py                # Fuel statistics and calculations
│   └── plots.py                # Graph generation with matplotlib/seaborn
│
├── main.py                     # Entry point to run the FastAPI app
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container setup for deployment
├── README.md                   # Project overview and instructions
└── .env                        # Environment variables (optional)

- models.py: Defines the structure of a fuel entry (date, liters, price, odometer, etc.)
- database.py: Creates and connects to the SQLite database
- routes.py: Exposes API endpoints like /fuel-entry, /stats, /plot
- utils.py: Calculates averages, fuel efficiency, cost per km
- plots.py: Generates graphs (e.g., fuel price over time)
- main.py: Starts the FastAPI server
- Dockerfile: Packages the app for deployment
- requirements.txt: Lists packages like fastapi, sqlite3, matplotlib, etc.
    