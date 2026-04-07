# Ecommerce Control Room UI

This folder contains the frontend for the ecommerce management options.

Quick start (fully functional)
1. Ensure MySQL is running and the schema is loaded from `e-commerce-management.sql`.
2. Install API dependencies:
	- `python3 -m pip install flask mysql-connector-python`
3. Start the backend from the project root:
	- `python3 server.py`
	- Or use another port: `PORT=5001 python3 server.py`
4. Open `http://localhost:5000` (or the port you chose) in your browser.

API mode
- Toggle demo mode off.
- If you serve the UI separately, set the API base URL (for example `http://localhost:5000`).
- The UI sends requests to endpoints like `/api/products` and `/api/insights/top-products`.

Database config (optional)
- `ECOM_DB_HOST`, `ECOM_DB_USER`, `ECOM_DB_PASSWORD`, `ECOM_DB_NAME`
