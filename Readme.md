# TankIQ – Fuel Logging System

TankIQ provides a simple and reliable system for fuel logging.  
It helps track fuel usage, costs, and efficiency over time, making record‑keeping and analysis straightforward.

This project follows:
- Airbnb JavaScript Style Guide for TypeScript
- PEP8 for Python

---


&nbsp;&nbsp;fuel_log.db                  # SQLite database  
&nbsp;&nbsp;main.py                      # Entry point to run the FastAPI app  
&nbsp;&nbsp;requirements.txt             # Python dependencies  
&nbsp;&nbsp;pyproject.toml               # Python project metadata  
&nbsp;&nbsp;Dockerfile                   # Containerization  
&nbsp;&nbsp;Makefile                     # Build/test automation  
&nbsp;&nbsp;package.json                 # Project metadata  
&nbsp;&nbsp;package-lock.json  
&nbsp;&nbsp;README.md                    # Project overview and instructions  

---

## Backend summary

### Core features
- Fuel entry management: CRUD operations via FastAPI routes.
- Statistics endpoint (/stats/): overall, monthly, and yearly fuel efficiency (km/L) and total cost.
- Metric consistency: system standardized to km/L (removed L/100km).
- Aggregated statistics: supports calculations for specific time periods.
- CSV export (/entries/export/): download entries with optional date range filters.

### Stability & reliability
- Error handling: fixed runtime errors (500s, validation errors, floating‑point issues).
- Import fix: corrected ImportError in app/server.py with explicit imports.
- Testing: comprehensive coverage across backend modules.

---

## Tests

- Unit tests (utils): calculate_entry_stats, get_overall_stats, get_best_efficiency, convert_entries_to_csv (includes empty input edge cases).
- Model tests (models): date format and non‑negative validators; schemas exercised (FuelEntryBase, FuelEntryDB, OverallStats, TimePeriodStats, DetailedStats, EntryList).
- Database tests (database.py): initialization, connection handling, delete_all_entries for populated and empty tables.
- API tests (api.py): FastAPI TestClient for CRUD (/entries/), stats (/stats/), and exports (/entries/export/) including empty DB and date‑filtered cases.

---

## Frontend summary

### Technology
- Framework: Vue 3 (Composition API, <script setup>)
- Routing: Vue Router
- State management: Pinia
- UI library: Naive UI
- Styling: Custom CSS + CSS Grid
- Build tool: Vite

### Layout & styling
- Sidebar: fixed/sticky, responsive width, styled hover/active states.
- Main area: unified background color, flush alignment with sidebar, subtle header separation.
- Grid layout: sidebar + main in one grid row, responsive stacking on narrow screens.
- File organization: styles centralized in main.css; slimmed App.vue.

---

## Statistics behavior

- Yearly charts: use monthly_stats aggregates for the selected year, sorted chronologically (old → new).
- Monthly charts: use raw store.entries within the selected month, sorted chronologically (old → new).
- Histogram: global efficiency distribution.
- Chart options: use buildOptions('month' | 'year') consistently.

---

## Improvement roadmap

### Current status
- Dashboard: stable
- Log: stable
- Stats: headline unified, spacing fixed, logic corrected


## How It Works

### 1. Input Files
- **Frontend Dockerfile**: Builds the UI using Node.js, then serves it with Nginx.
- **Backend Dockerfile**: Builds and runs the FastAPI backend with Python.
- **nginx.conf**: Configures Nginx to handle frontend routing correctly.
- **docker-compose.yml**: Defines how frontend and backend containers run together.
- **Makefile**: Provides shortcuts for Docker Compose lifecycle management.

### 2. Execution Flow
- Dockerfiles define how each service is built and run.
- `docker-compose.yml` orchestrates both services together.
- The Makefile provides simple commands (`make build`, `make up`, `make down`, etc.) to manage containers.
- Developers can rebuild, restart, clean, or view logs without typing long Docker commands.

### 3. CLI Interface
- With `make` installed, you can run:
  
      make build
      make up
      make down
      make logs
      make frontend
      make backend
      make restart
      make clean

- Without `make`, use equivalent Docker Compose commands:

      docker compose build
      docker compose up -d
      docker compose down
      docker compose logs -f

---

## Docker Usage

To build and run the services directly with Docker Compose:

    docker compose build
    docker compose up -d

To stop and remove containers:

    docker compose down

To rebuild everything from scratch:

    docker compose down
    docker compose build --no-cache
    docker compose up -d

To clean containers, images, and volumes:

    docker compose down --volumes --remove-orphans
    docker system prune -af

---

## Makefile Usage

The Makefile simplifies common tasks. Ensure you have `make` installed (Linux/macOS usually include it; on Windows install via Chocolatey, Git Bash with MSYS2, or WSL).

To build images:

    make build

To start containers:

    make up

To stop containers:

    make down

To view logs:

    make logs

To view frontend logs:

    make frontend

To view backend logs:

    make backend

To restart everything:

    make restart

To clean containers, images, and volumes:

    make clean

---

## Local Development

If you prefer not to use Docker, you can run the backend locally with Python and the frontend with Node.js.

### Backend
1. Create a virtual environment:

       python3 -m venv venv

2. Activate the environment:

   - On macOS/Linux:

         source venv/bin/activate

   - On Windows:

         venv\Scripts\activate

3. Install dependencies:

       pip install -r requirements.txt

4. Run the FastAPI app:

       uvicorn main:app --reload

### Frontend
1. Navigate to the `ui/` directory.
2. Install dependencies:

       npm install

3. Run the development server:

       npm run dev

---

## Summary
- **Dockerfiles** define how to build and run frontend and backend services.
- **nginx.conf** ensures frontend routing works.
- **docker-compose.yml** orchestrates both services.
- **Makefile** provides shortcuts for building, running, restarting, and cleaning containers.
- You can run everything with Docker Compose or locally with Python and Node.js.

