# CS 425 Final Project – Real Estate Management Web Application

## 1. Overview

This is a small **web application** that demonstrates the relational schema and ER design for a **Real Estate Management** system.

The app is built for the CS 425 final project and shows how the schema is used in a real application:

- **Register renters** (inserts into `Users` and `Renter`).
- **Browse and search properties** (joins `Property` with `Neighbourhood` and subtype tables).
- **Create bookings with credit cards** (inserts into `CreditCard`, `Booking`, `Rewards`, `Books`, and updates `Property.Availability`).
- **Renter dashboard** with total reward points and list of bookings.

---

## 2. Technology Stack

- **Backend:** Python 3 + Flask
- **Database:** PostgreSQL
- **Templating:** Jinja2 HTML templates (no separate React frontend – keeps setup simple)
- **ORM / DB access:** `psycopg2` (raw SQL queries)

---

## 3. Project Structure

```text
realestate_app/
├── app.py              # Main Flask application
├── config.py           # Database connection settings (host, db, user, password, port)
├── requirements.txt    # Python package dependencies
├── schema.sql          # SQL script to create tables and insert sample data
├── README.md           # This file
├── run_app.bat         # Optional helper to start the app on Windows
└── templates/          # HTML templates for the Flask app
    ├── base.html
    ├── home.html
    ├── new_booking.html
    ├── new_renter.html
    ├── properties.html
    └── renter_dashboard.html
```

> **Note:**  
> `config.py` contains DB connection settings. If needed, these can be edited to match the local PostgreSQL installation.

---

## 4. Prerequisites

To run this application, you need:

1. **Python 3.10+** (tested with Python 3.11)
2. **pip** (Python package manager)
3. **PostgreSQL** (recommended: version 13 or above)

Optional (but helpful for development):

- **conda / Anaconda** for managing environments  
- A code editor like **VS Code**

---

## 5. Database Setup (PostgreSQL)

### 5.1. Create the database

1. Open **SQL Shell (psql)** or another PostgreSQL client.
2. Connect as a user with permission to create databases (e.g. `postgres`).
3. Run:

   ```sql
   CREATE DATABASE realestate;
   ```

4. Connect to the new database:

   ```sql
   \c realestate
   ```

### 5.2. Run the schema script

Inside `psql`, run the provided schema script to create tables and insert sample data.

If the project is located at:

```text
C:\Susmeet proj\realestate_app
```

then execute:

```sql
\cd 'C:/Susmeet proj/realestate_app'
\i schema.sql
```

This will:

- Create all the required tables (`Users`, `Renter`, `Agent`, `Neighbourhood`, `Property`, `House`, `Apartment`, `CommercialBuilding`, `Land`, `VacationHouse`, `CreditCard`, `Booking`, `Rewards`, `Books`, etc.).
- Insert sample data into the tables.

You can verify that tables exist and contain data:

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public';

SELECT * FROM Users LIMIT 5;
SELECT * FROM Property LIMIT 5;
```

---

## 6. Configure the application (`config.py`)

Open `config.py` in the project root and check/update these values:

```python
DB_HOST = "localhost"
DB_NAME = "realestate"
DB_USER = "postgres"          # or another PostgreSQL user
DB_PASSWORD = "your_password" # replace with the actual password
DB_PORT = 5432                # replace with your port number
```

These must match the PostgreSQL installation used to create the `realestate` database.

---

## 7. Python Environment & Dependencies

### Option A – Using virtualenv / venv (generic)

From the project folder:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Option B – Using conda (recommended for development, optional for running)

```bash
conda create -n realestate_app_env python=3.11 -y
conda activate realestate_app_env
pip install -r requirements.txt
```

After this, all required packages (Flask, psycopg2, etc.) will be installed.

---

## 8. Running the Application

### Option 1 – Command line

From the project folder (after activating the environment):

```bash
set FLASK_APP=app.py       # on Windows CMD
set FLASK_DEBUG=1          # optional, for debug mode
flask run
```

Or in PowerShell:

```powershell
$env:FLASK_APP = "app.py"
$env:FLASK_DEBUG = "1"
flask run
```

You should see output similar to:

```text
 * Serving Flask app 'app.py'
 * Running on http://127.0.0.1:5000
```

Open a browser and go to:

```text
http://127.0.0.1:5000/
```

### Option 2 – Double-click `run_app.bat` (Windows)

If `run_app.bat` is present and dependencies are installed, simply double-click it.  
It will:

- Navigate to the project directory
- Set `FLASK_APP=app.py`
- Run `flask run`

(See the next section for `run_app.bat` contents.)

---

## 9. Application Walk-through (Demo Script)

Once the server is running:

1. Go to **Home** (`/`)
   - Brief explanation of project and features.

2. Go to **Register Renter**
   - Fill in an email, name, and optional details.
   - This inserts/updates in `Users` and `Renter`.

3. Go to **Browse Properties**
   - Shows all properties, with filters for city and price.
   - Columns include property type, price, neighbourhood, agent, availability.

4. Go to **New Booking**
   - Enter the renter’s email, select an available property, and enter card details.
   - This will:
     - Insert into `CreditCard` (if not already present).
     - Insert a `Booking`.
     - Insert a `Rewards` row with reward points based on property price.
     - Insert a row into `Books` (link between renter and property).
     - Set `Property.Availability = FALSE`.

5. View **Renter Dashboard** (by URL)
   - Navigate to: `/renters/<renter_email>`
   - Example: `http://127.0.0.1:5000/renters/test@example.com`
   - Shows renter profile, total reward points, and booking history.

This flow demonstrates CRUD operations, joins across multiple tables, updates, and basic aggregation.

---

## 10. Troubleshooting

**Common issues:**

1. **Database connection error (`OperationalError`)**
   - Check that PostgreSQL is running.
   - Confirm `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, and `DB_PORT` in `config.py`.

2. **`relation "users" does not exist`**
   - The schema script was not run on the `realestate` database.
   - Reconnect to `realestate` in `psql` and run `\i schema.sql` again.

3. **Port already in use**
   - Another process might be using port 5000.
   - Stop that process or run Flask on a different port:
     ```bash
     flask run --port 5001
     ```

---

## 11. Notes for Grading / Reviewers

- The application **directly uses** the relational schema from the project’s ER diagram.
- Tables touched include:
  - `Users`, `Renter`, `Neighbourhood`, `Property` and its subtypes
  - `CreditCard`, `Booking`, `Rewards`, `Books`
- The code demonstrates:
  - Inserts with conflict handling (upsert)
  - Multi-table joins
  - Updates and simple transactional logic
  - Aggregation (sum of reward points)
- The source code is contained within a single Flask application (`app.py`) and Jinja2 templates (in `templates/`).
