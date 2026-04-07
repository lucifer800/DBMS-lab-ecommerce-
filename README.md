# DBMS Ecommerce Lab Project

A simple ecommerce management system with a Flask API and a bold, single-page UI.

## Run locally

1. Load schema + seed data:
   - `mysql -u root -p < e-commerce-management.sql`
2. Install dependencies:
   - `python3 -m pip install -r requirements.txt`
3. Start the backend:
   - `python3 server.py`
4. Open `http://localhost:5000` and toggle Demo mode off.

## Environment variables

Backend (server.py):
- `PORT` (default `5000`)
- `ECOM_DB_HOST` (default `localhost`)
- `ECOM_DB_PORT` (default `3306`)
- `ECOM_DB_USER` (default `root`)
- `ECOM_DB_PASSWORD` (default `12345678`)
- `ECOM_DB_NAME` (default `ecommerce_db`)
- `ECOM_DB_SSL_CA` (optional, file path)
- `ECOM_DB_SSL_DISABLED` (`true` or `false`)
- `ECOM_DB_SSL_VERIFY` (`true` or `false`)

Frontend:
- Use the "Set API base" button to point to your hosted backend URL. The UI stores it in local storage.

## Deploy (recommended)

### 1) Host the MySQL database
Pick one MySQL host (Railway, Aiven, PlanetScale). Create a database and note:
- Host, port, database name
- Username + password
- SSL requirements (if any)

#### Export your local data
- `mysqldump -u root -p ecommerce_db > ecommerce_dump.sql`

#### Import into hosted MySQL
- `mysql -h <HOST> -P <PORT> -u <USER> -p <DB_NAME> < ecommerce_dump.sql`

### 2) Deploy the backend (Render or Railway)
- Connect this GitHub repo.
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn server:app`
- Set environment variables:
  - `PORT` (Render/Railway sets this automatically)
  - `ECOM_DB_HOST`, `ECOM_DB_PORT`, `ECOM_DB_USER`, `ECOM_DB_PASSWORD`, `ECOM_DB_NAME`
  - `ECOM_DB_SSL_CA` if your host requires SSL

### 3) Deploy the frontend (Vercel)
- Import the same repo in Vercel.
- Set **Root Directory** to `web`.
- Deploy.
- Open the site, toggle Demo mode off, and set API base to your backend URL.
