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
|    │    │    └── api-services.ts     
|    │    ├── stores/                
|    │    │    ├── fuel-store.ts
|    │    │    └── layout-store.ts  
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


## Statistics Screen


## Log Screen


# Project Progress

# We split the single isLoading flag into isLoadingEntries and isLoadingStats so Dashboard and Stats can load independently without overwriting each other.

# Fuel Tracker Improvement Roadmap

## ✅ Current Status
- **Dashboard**: looks fine, no major changes needed  
- **Log**: also fine  

## 🔧 Improvements Needed
1. **Statistics**
   - Efficiency graph needs fixing (currently left-to-right, should be right-to-left for your locale).
   - Graph orientation should respect language/region settings.

2. **Monthly & Yearly Filters**
   - Add ability to **choose a specific month**.
   - Same for **year selection** (instead of showing all data).

3. **Currency Configuration**
   - Currency should be **configurable as an argument** (e.g., `--currency=USD` or via settings).
   - This allows localization and flexibility.

4. **Summary Table**
   - Currently shows **all entries unnecessarily**.
   - Should instead show **monthly totals** (liters, cost, distance).
   - Insights (efficiency, averages, anomalies) should follow the summary.

5. **Export & Purge Options**
   - Add **export** (CSV/JSON) for backups or analysis.
   - Add **purge database** option for resetting/cleaning data.

6. **Dark Mode**
   - Implement a **dark theme toggle** for better UX.

7. **Deployment**
   - **Docker image**: containerize the app for easy deployment.
   - **Makefile**: automate build, test, and deployment steps.

## 🚀 Suggested Next Steps
- **Prioritize UX fixes first**: statistics graph orientation, summary table, filters.  
- **Then add configuration options**: currency, export/purge.  
- **Finally tackle deployment & theming**: dark mode, Docker, Makefile.  


========================================================
                 FUEL EFFICIENCY REPORT
========================================================

[ CONTROLS ]
--------------------------------------------------------
View: [ Yearly ▾ | Monthly ▾ ]
If Yearly → Period: [ YYYY ▾ ]
If Monthly → Period: [ YYYY-MM ▾ ]

========================================================

EXECUTIVE SUMMARY
--------------------------------------------------------
This report summarizes fuel efficiency and costs for the selected period. 
Vehicles traveled a total of XXXX km, with an overall efficiency of XX km/L. 
Total spending reached $XXXX, reflecting the combined fuel costs for this period. 
Compared to previous periods, efficiency was higher/lower, and costs rose/fell accordingly.

========================================================

YEARLY ANALYSIS (View = Yearly)
--------------------------------------------------------
Fuel Efficiency Trends → [ Bar Chart, ordered oldest → newest ]
Fuel Cost Trends       → [ Line Chart, ordered oldest → newest ]

Yearly Summary Table (only selected year)
--------------------------------------------------------
Year | Efficiency (km/L) | Distance (km) | Total Cost
--------------------------------------------------------
2024 |        XX         |     XXXX      | $XXXX

Insights
--------------------------------------------------------
Efficiency in 2024 averaged XX km/L, which is above/below the long‑term trend.  
Total distance reached XXXX km, showing increased usage compared to earlier years.  
Fuel costs of $XXXX were higher/lower than the multi‑year average, reflecting price or demand changes.

========================================================

MONTHLY ANALYSIS (View = Monthly)
--------------------------------------------------------
Fuel Efficiency Trends → [ Line Chart, ordered Jan → Dec ]
Fuel Cost Trends       → [ Line Chart, ordered Jan → Dec ]

Monthly Summary Table (only selected month)
--------------------------------------------------------
Month | Efficiency (km/L) | Fuel Cost | Price/L
--------------------------------------------------------
Mar   |        XX         |   $XXX    | $X.XX

Insights
--------------------------------------------------------
In March 2024, efficiency was XX km/L, slightly above/below the yearly average.  
Vehicles traveled XXXX km, consistent with seasonal driving patterns.  
Fuel spending of $XXX was unusually high/low compared to other months in the same year.

========================================================
END OF REPORT
========================================================