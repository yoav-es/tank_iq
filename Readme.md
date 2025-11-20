This project provides a simple and reliable system for fuel logging.  
It helps track fuel usage, costs, and efficiency over time, making record‑keeping and analysis straightforward.  

This project follows the Airbnb JavaScript Style Guide for typescript and pep8 for python


TankIQ/
├── app/                        # Core application logic
│   ├── __init__.py             # Initializes the app package
│   ├── models.py               # Defines FuelEntry class and data schema
│   ├── database.py             # Handles SQLite connection and setup
│   ├── routes.py               # FastAPI endpoints for CRUD operations
│   ├── utils.py                # Fuel statistics and calculations
│   └── plots.py                # Graph generation with matplotlib/seaborn
├── tests/                      
├── ui/                         
|    ├── src 
|    │    ├── router/                
|    │    │    └── index.ts           
|    │    ├── services/              
|    │    │    └── apiServices.ts     
|    │    ├── stores/                
|    │    │    ├── fuelStore.ts
|    │    │    └── layoutStore.ts  
|    │    ├── types/                  
|    │    │    └── fuelEntry.ts  
|    │    ├── views/                  
|    │    │    ├── dashboard-view.vue
|    │    │    ├── log-view.vue
|    │    │    └── stats-view.vue
|    |    ├── App.vue
|    |    ├── main.css
|    |    └── main.ts
|    |      
|    ├── index.html
|    ├── package-lock.json
|    ├── package.json
|    ├── tsconfig.json
|    └── vite.comfig.json
|
├── fuel_log.db 
├── main.py                     # Entry point to run the FastAPI app
├── requirements.txt            # Python dependencies
├── package-lock.json
├── package.json
├── pyproject.tomel
├── package.json
└── README.md                   # Project overview and instructions

- models.py: Defines the structure of a fuel entry (date, liters, price, odometer, etc.)
- database.py: Creates and connects to the SQLite database
- routes.py: Exposes API endpoints like /fuel-entry, /stats, /plot
- utils.py: Calculates averages, fuel efficiency, cost per km
- plots.py: Generates graphs (e.g., fuel price over time)
- main.py: Starts the FastAPI server
- Dockerfile: Packages the app for deployment
- requirements.txt: Lists packages like fastapi, sqlite3, matplotlib, etc.
    
# 🌟 TankIQ Backend Final Summary

## I. Core Feature Implementation & Metric Consistency

This phase finalized the core functionality of the TankIQ Fuel Tracker API, ensuring all components work together seamlessly and adhere to the $\text{km/L}$ standard.

- **Statistical Insights:** Finalized the **`/stats/` endpoint** to calculate and return comprehensive overall, monthly, and yearly fuel efficiency statistics ($\text{km/L}$ and total cost).
- **New Feature Implemented:** Added the ability to calculate and display aggregated statistics for specific time periods.
- **Metric Consistency:** The application logic, database storage, API inputs/outputs, and overall statistics are now strictly consistent across the **$\text{km/L}$ metric**. The old $\text{L/100km}$ metric has been entirely removed and verified absent in all responses.
- **Data Structure Fixes:** Resolved Pydantic model mismatches and key errors (`KeyError: 'month'`, `KeyError: 'year'`) in utility functions and tests to ensure clean data flow.

## II. Stability, Reliability, and Testing

Critical stability fixes and a comprehensive test suite ensure the API is robust and production-ready:

- **Robust Error Handling:** All critical runtime errors (500 Internal Server Errors, ResponseValidationErrors, and floating-point assertion errors) were identified and fixed, resulting in a **highly stable API**.
- **Crucial Stability Fix:** Corrected the tricky **`ImportError`** in `app/server.py` using an explicit module import, ensuring the API is stable across all testing and deployment environments.
- **Comprehensive Test Coverage:** A full test suite was implemented and verified, confirming the integrity of the application at three levels:
    - **Unit Tests:** Verify calculation utilities.
    - **Integration Tests:** Verify database CRUD operations.
    - **Functional API Tests:** Use TestClient to verify all HTTP routes, status codes, and complex statistical calculations.

# Project Summary (UI Work Session)

## Technology & Framework
- **Frontend Framework:** Vue 3 (Composition API, `<script setup>` syntax)
- **Routing:** Vue Router for navigation between views
- **State Management:** Pinia store (`useLayoutStore`) for menu state
- **UI Library / GUI Framework:** Naive UI (`n-layout`, `n-menu`, `n-config-provider`, etc.)
- **Styling:** Custom CSS with CSS Grid for layout, responsive design via media queries
- **Build Tool:** Vite (standard for Vue 3 projects)

## Sidebar
- Converted to a fixed/sticky element so it stays visible while scrolling
- Narrowed width (`clamp(100px, 12vw, 160px)`)
- Dark background with white/blue text for contrast
- Menu styling updated for hover/active states

## Main Area
- Unified background color (`#e5e7eb`) across `html`, `body`, `#app`, `.app-layout`, `.main`, and `.main-content`
- Eliminated white gaps when scrolling
- Header uses a slightly darker gray (`#d1d5db`) for subtle separation
- Removed margin/padding offsets so the main screen aligns flush at the top with the sidebar header/menu

## Layout
- Replaced margin‑based offset with a proper CSS Grid (`grid-template-columns: sidebar + main`)
- Sidebar and main area explicitly placed in the same grid row for top alignment
- Responsive rules: sidebar stacks above main content on narrow screens

## File Organization
- Moved all styles into a dedicated `main.css` file
- `App.vue` slimmed down to template + script only
- `main.ts` imports `main.css` globally

# Fuel Tracker App Wireframes

---

## Dashboard (Default Landing)

+-------------------------------------------------------------+
| Sidebar (20%)        | Dashboard (Default Page)             |
| -------------------  | -----------------------------------  |
| • Dashboard (active) |   [ Graph: Avg Fuel Consumption ]    |
| • Fuel Log           |   --------------------------------   |
| • Statistics         |   Efficiency Trend Over Time         |
|                      |                                      |
| (icons + text)       |   [ Data Cards Row ]                 |
|                      |   --------------------------------   |
|                      |   | Current Avg | Best Month | Dist | |
|                      |   | 6.8 L/100km | 5.9 L/100km|2450km| |
|                      |   --------------------------------   |
+-------------------------------------------------------------+
| Footer (spans full width)                                   |
| Quick Links | Export CSV | Dark Mode Toggle                 |
+-------------------------------------------------------------+

---

## Statistics Screen

+-------------------------------------------------------------+
| Sidebar (20%)        | Statistics                           |
| -------------------  | -----------------------------------  |
| • Dashboard          |   [ View Selector ]                  |
| • Fuel Log           |   --------------------------------   |
| • Statistics (active)|   | Monthly | Yearly | Custom Range | |
|                      |   --------------------------------   |
| (icons + text)       |   [ Date Range Picker ]              |
|                      |   --------------------------------   |
|                      |   | From: [____]  To: [____]        |
|                      |   --------------------------------   |
|                      |                                      |
|                      |   [ Chart Area ]                     |
|                      |   --------------------------------   |
|                      |   | Line Chart: Avg Consumption      |
|                      |   | (L/100km or km/L over time)      |
|                      |   --------------------------------   |
|                      |                                      |
|                      |   [ Summary Cards ]                  |
|                      |   --------------------------------   |
|                      |   | Highest Efficiency | Lowest Eff. |
|                      |   | Avg Consumption    | Total Dist. |
|                      |   --------------------------------   |
+-------------------------------------------------------------+
| Footer (spans full width)                                   |
| Export CSV | Export PDF | Dark Mode Toggle                  |
+-------------------------------------------------------------+

---

## Log Screen

+-------------------------------------------------------------+
| Sidebar (20%)        | Fuel Log                             |
| -------------------  | -----------------------------------  |
| • Dashboard          |   [ Fuel Log Title ]                 |
| • Fuel Log (active)  |   --------------------------------   |
| • Statistics         |   [ Add Entry ] [ Update Entry ]     |
|                      |   [ Delete Entry ]                   |
| (icons + text)       |   --------------------------------   |
|                      |   Recent Entries Table               |
|                      |   --------------------------------   |
|                      |   | Date | Liters | Price/L | Dist | |
|                      |   | 2025-11-14 | 40 | 6.5 | 520km | |
|                      |   | 2025-11-20 | 35 | 6.4 | 460km | |
|                      |   | 2025-11-25 | 42 | 6.6 | 540km | |
|                      |   --------------------------------   |
|                      |   Pagination / “View More”           |
+-------------------------------------------------------------+
| Footer (spans full width)                                   |
| Quick Links | Export CSV | Dark Mode Toggle                 |
+-------------------------------------------------------------+