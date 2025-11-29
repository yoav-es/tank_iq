# 🚗 TankIQ – Fuel Logging System

TankIQ provides a **simple and reliable system for fuel logging**.  
It helps track fuel usage, costs, and efficiency over time, making record‑keeping and analysis straightforward.

This project follows:
- **Airbnb JavaScript Style Guide** for TypeScript
- **PEP8** for Python

---

## 📂 Project Structure

# 📂 Project Structure – TankIQ

- TankIQ/
  - app/                         # Core application logic
      - __init__.py              # Initializes the app package
      - models.py                # Defines Pydantic schemas for entries and statistics
      - database.py              # Manages SQLite connection, schema initialization, and CRUD operations
      - api.py                   # FastAPI router with CRUD endpoints, stats, and CSV export
      - server.py                # FastAPI app initialization, logging, lifespan events, and CORS middleware
      - utils.py                 # Helper functions for calculations, statistics, and CSV conversion
  - `tests/`                      # Unit, integration, and functional tests
    - `test_utils.py`             # Unit tests for utility functions
    - `test_models.py`            # Validation and schema tests for Pydantic models
    - `test_database.py`          # Integration tests for SQLite database operations
    - `test_api.py`               # Functional tests for FastAPI endpoints (CRUD, stats, export)  - ui/                          # Vue 3 frontend
    - src/
      - router/
        - index.ts               # Vue Router setup
      - services/
        - api-services.ts        # API service layer
      - stores/
        - fuel-store.ts          # Pinia store for fuel entries
        - layout-store.ts        # Pinia store for layout state
      - types/
        - fuelEntry.ts           # TypeScript type definitions
      - views/
        - dashboard-view.vue
        - log-view.vue
        - stats-view.vue
      - App.vue
      - main.css
      - main.ts
    - index.html
    - package-lock.json
    - package.json
    - tsconfig.json
    - vite.config.json
  - fuel_log.db                  # SQLite database
  - main.py                      # Entry point to run the FastAPI app
  - requirements.txt             # Python dependencies
  - pyproject.toml               # Python project metadata
  - Dockerfile                   # Containerization
  - Makefile                     # Build/test automation
  - package-lock.json
  - package.json
  - README.md                    # Project overview and instructions

---

## ⚙️ Backend Summary

### Core Features
- **Fuel Entry Management:** CRUD operations via FastAPI routes.
- **Statistics Endpoint (`/stats/`):** Returns overall, monthly, and yearly fuel efficiency statistics in **km/L** and total cost.
- **Metric Consistency:** Entire system standardized to **km/L** (removed old L/100km metric).
- **Aggregated Statistics:** Supports calculations for specific time periods.
- **CSV Export (`/entries/export/`):** Download entries as CSV, with optional date range filters.

### Stability & Reliability
- **Error Handling:** Fixed runtime errors (500s, validation errors, floating‑point issues).
- **Import Fix:** Corrected `ImportError` in `app/server.py` with explicit imports.
- **Testing:** Comprehensive coverage across all backend modules.

---
## 🧪 Tests

The backend is fully covered by automated tests:

- **Unit Tests (utils):**  
  Validate calculation helpers (`calculate_entry_stats`, `get_overall_stats`, `get_best_efficiency`, `convert_entries_to_csv`) including edge cases like empty input.

- **Model Tests (models):**  
  Ensure Pydantic validators enforce correct date formats and non‑negative values. All schemas (`FuelEntryBase`, `FuelEntryDB`, `OverallStats`, `TimePeriodStats`, `DetailedStats`, `EntryList`) are exercised.

- **Database Tests (database.py):**  
  Cover initialization, connection handling, and deletion logic (`delete_all_entries`) with both populated and empty tables.

- **API Tests (api.py):**  
  Functional tests using FastAPI’s `TestClient`:
  - CRUD endpoints (`/entries/`)  
  - Statistics endpoint (`/stats/`)  
  - Export endpoint (`/entries/export/`) including empty DB and date‑filtered exports  
---

## 🎨 Frontend Summary

### Technology
- **Framework:** Vue 3 (Composition API, `<script setup>`)
- **Routing:** Vue Router
- **State Management:** Pinia
- **UI Library:** Naive UI
- **Styling:** Custom CSS + CSS Grid
- **Build Tool:** Vite

### Layout & Styling
- **Sidebar:** Fixed/sticky, responsive width, styled hover/active states.
- **Main Area:** Unified background color, flush alignment with sidebar, subtle header separation.
- **Grid Layout:** Sidebar + main aligned in one grid row, responsive stacking on narrow screens.
- **File Organization:** Styles centralized in `main.css`, slimmed `App.vue`.

### Headline Consistency (Work Done Today)
- Unified **headline structure** across `dashboard-view`, `log-view`, and `stats-view`.
- Removed old `report__header` block from stats view.
- Eliminated extra spacing by aligning separator margins.
- Introduced a **shared headline style** for consistency across modules.

---

## 🛠️ Improvement Roadmap

### ✅ Current Status
- **Dashboard:** Stable  
- **Log:** Stable  
- **Stats:** Headline unified, spacing fixed  

### 🔧 Next Improvements
1. **Statistics**
   - Fix efficiency graph orientation (respect locale).
   - Ensure monthly/yearly filters allow specific selection.
2. **Currency Configuration**
   - Add configurable currency option (`--currency=USD` or via settings).
3. **Summary Table**
   - Show monthly totals (liters, cost, distance).
   - Insights follow summary.
4. **Export & Purge**
   - Export data (CSV/JSON).
   - Purge/reset database option.
5. **Dark Mode**
   - Add theme toggle.
6. **Deployment**
   - Docker image for deployment.
   - Makefile for build/test automation.

---

## 📝 Work Session Summary

- **Frontend:**  
  - Unified headline styles across all views.  
  - Removed unused `report__header` styles.  
  - Fixed spacing issues in stats view.  

- **Backend:**  
  - Stable API with consistent km/L metric.  
  - Comprehensive test coverage.  

- **Roadmap:**  
  - Focus on statistics visualization, filters, currency config, and deployment packaging.
