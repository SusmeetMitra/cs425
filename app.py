from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
import psycopg2.extras
import config  # your config.py
from decimal import Decimal
import traceback

app = Flask(__name__)
app.secret_key = "change-this-secret-key"  # required for flash messages


# ---------- DATABASE CONNECTION ----------

def get_db_connection():
    conn = psycopg2.connect(
        host=config.DB_HOST,
        database=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        port=config.DB_PORT,
    )
    return conn


def get_next_id(cur, table_name, id_column):
    """
    Returns next integer ID for a table/column, works with both
    normal cursor and RealDictCursor.
    """
    query = f"SELECT COALESCE(MAX({id_column}), 0) + 1 AS next_id FROM {table_name};"
    cur.execute(query)
    row = cur.fetchone()

    if row is None:
        return 1

    # RealDictCursor => row is a dict
    if isinstance(row, dict):
        return row["next_id"]

    # Regular cursor => row is a tuple
    return row[0]


@app.route("/")
def home():
    return render_template("home.html")


# ---------- REGISTER NEW RENTER (Users + Renter) ----------

@app.route("/renters/new", methods=["GET", "POST"])
def new_renter():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        first_name = request.form.get("first_name", "").strip()
        address = request.form.get("address", "").strip()
        move_in_date = request.form.get("move_in_date")
        preferred_location = request.form.get("preferred_location", "").strip()
        budget = request.form.get("budget")

        if not email or not first_name:
            flash("Email and first name are required.")
            return redirect(url_for("new_renter"))

        conn = get_db_connection()
        cur = conn.cursor()

        try:
            # Users
            cur.execute(
                """
                INSERT INTO Users (Email, First_name, Address)
                VALUES (%s, %s, %s)
                ON CONFLICT (Email) DO UPDATE
                    SET First_name = EXCLUDED.First_name,
                        Address = EXCLUDED.Address;
                """,
                (email, first_name, address),
            )

            # Renter
            cur.execute(
                """
                INSERT INTO Renter (Email, Move_In_Date, Preferred_Location, Budget)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (Email) DO UPDATE
                    SET Move_In_Date = EXCLUDED.Move_In_Date,
                        Preferred_Location = EXCLUDED.Preferred_Location,
                        Budget = EXCLUDED.Budget;
                """,
                (email, move_in_date, preferred_location, budget),
            )

            conn.commit()
            flash("Renter registered/updated successfully.")
        except Exception as e:
            conn.rollback()
            flash(f"Error while saving renter: {e}")
        finally:
            cur.close()
            conn.close()

        return redirect(url_for("home"))

    return render_template("new_renter.html")


# ---------- BROWSE / SEARCH PROPERTIES ----------

@app.route("/properties")
def list_properties():
    city = request.args.get("city", "").strip()
    min_price = request.args.get("min_price", "").strip()
    max_price = request.args.get("max_price", "").strip()
    only_available = request.args.get("only_available")

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    base_query = """
        SELECT
            p.property_id,
            p.location,
            p.city,
            p.state,
            p.price,
            p.availability,
            n.zip_code,
            n.crime_rate,
            n.nearby_schools,
            u.first_name AS agent_name,
            CASE
                WHEN h.property_id IS NOT NULL THEN 'House'
                WHEN a.property_id IS NOT NULL THEN 'Apartment'
                WHEN cb.property_id IS NOT NULL THEN 'Commercial Building'
                WHEN lnd.property_id IS NOT NULL THEN 'Land'
                WHEN v.property_id IS NOT NULL THEN 'Vacation House'
                ELSE 'Unknown'
            END AS property_type
        FROM Property p
        LEFT JOIN Neighbourhood n ON n.zip_code = p.zip_code
        LEFT JOIN Users u ON u.email = p.agent_email
        LEFT JOIN House h ON h.property_id = p.property_id
        LEFT JOIN Apartment a ON a.property_id = p.property_id
        LEFT JOIN CommercialBuilding cb ON cb.property_id = p.property_id
        LEFT JOIN Land lnd ON lnd.property_id = p.property_id
        LEFT JOIN VacationHouse v ON v.property_id = p.property_id
        WHERE 1=1
    """

    params = []

    if city:
        base_query += " AND p.city ILIKE %s"
        params.append(f"%{city}%")

    if min_price:
        base_query += " AND p.price >= %s"
        params.append(min_price)

    if max_price:
        base_query += " AND p.price <= %s"
        params.append(max_price)

    if only_available == "on":
        base_query += " AND p.availability = TRUE"

    base_query += " ORDER BY p.city, p.price;"

    cur.execute(base_query, tuple(params))
    properties = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "properties.html",
        properties=properties,
        city=city,
        min_price=min_price,
        max_price=max_price,
        only_available=only_available,
    )


# ---------- CREATE BOOKING + REWARDS ----------

@app.route("/bookings/new", methods=["GET", "POST"])
def new_booking():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    if request.method == "POST":
        renter_email = request.form.get("renter_email", "").strip()
        property_id = request.form.get("property_id")
        card_number = request.form.get("card_number", "").strip()
        card_holder = request.form.get("card_holder", "").strip()
        cvv = request.form.get("cvv", "").strip()
        exp_date = request.form.get("exp_date")  # YYYY-MM-DD

        try:
            # 1) Check renter exists
            cur.execute("SELECT 1 FROM Renter WHERE Email = %s;", (renter_email,))
            if not cur.fetchone():
                flash("Renter does not exist. Please register renter first.")
                return redirect(url_for("new_booking"))

            # 2) Check property exists and is available, get price
            cur.execute(
                "SELECT price, availability FROM Property WHERE Property_ID = %s;",
                (property_id,),
            )
            prop = cur.fetchone()
            if not prop:
                flash("Property not found.")
                return redirect(url_for("new_booking"))

            if not prop["availability"]:
                flash("Property is not available.")
                return redirect(url_for("new_booking"))

            # price is a Decimal from PostgreSQL
            raw_price = prop["price"]
            # Ensure we have a Decimal and not None
            if raw_price is None:
                price = Decimal("0")
            elif isinstance(raw_price, Decimal):
                price = raw_price
            else:
                # Convert other numeric types to Decimal via string to be safe
                price = Decimal(str(raw_price))

            # 3) Upsert credit card
            cur.execute(
                "SELECT 1 FROM CreditCard WHERE Card_Number = %s;",
                (card_number,),
            )
            if not cur.fetchone():
                cur.execute(
                    """
                    INSERT INTO CreditCard
                    (Card_Number, Card_Holder_Name, Email, CVV, EXP_Date)
                    VALUES (%s, %s, %s, %s, %s);
                    """,
                    (card_number, card_holder, renter_email, cvv, exp_date),
                )

            # 4) New booking row
            booking_id = get_next_id(cur, "Booking", "Booking_ID")
            cur.execute(
                """
                INSERT INTO Booking (Booking_ID, Card_Number, Property_ID, Booking_Date)
                VALUES (%s, %s, %s, CURRENT_DATE);
                """,
                (booking_id, card_number, property_id),
            )

            # 5) Rewards: 1% of price as integer points
            # e.g., price = 9500000.00 -> 95000 points
            points = int(price * Decimal("0.01"))

            reward_id = get_next_id(cur, "Rewards", "Reward_ID")
            cur.execute(
                """
                INSERT INTO Rewards (Reward_ID, Booking_ID, Email, Points_Balance)
                VALUES (%s, %s, %s, %s);
                """,
                (reward_id, booking_id, renter_email, points),
            )

            # 6) Books (link renter to property)
            cur.execute(
                """
                INSERT INTO Books (Renter_Email, Property_ID)
                VALUES (%s, %s)
                ON CONFLICT (Renter_Email, Property_ID) DO NOTHING;
                """,
                (renter_email, property_id),
            )

            # 7) Mark property unavailable
            cur.execute(
                "UPDATE Property SET Availability = FALSE WHERE Property_ID = %s;",
                (property_id,),
            )

            conn.commit()
            flash(
                f"Booking created! ID={booking_id}, Reward points earned={points}."
            )
        except Exception as e:
            conn.rollback()
            # Print full traceback to your terminal so you can see real error
            print("Error while creating booking:", repr(e))
            traceback.print_exc()
            flash(f"Error while creating booking: {e}")
        finally:
            cur.close()
            conn.close()

        return redirect(url_for("home"))

    # GET: list available properties for the form
    cur.execute(
        """
        SELECT property_id, location, city, state, price
        FROM Property
        WHERE availability = TRUE
        ORDER BY city, price;
        """
    )
    properties = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("new_booking.html", properties=properties)


# ---------- RENTER DASHBOARD ----------

@app.route("/renters/<email>")
def renter_dashboard(email):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # Renter + user info
    cur.execute(
        """
        SELECT u.email, u.first_name, u.address,
               r.move_in_date, r.preferred_location, r.budget
        FROM Renter r
        JOIN Users u ON u.email = r.email
        WHERE r.email = %s;
        """,
        (email,),
    )
    renter = cur.fetchone()
    if not renter:
        cur.close()
        conn.close()
        flash("Renter not found.")
        return redirect(url_for("home"))

    # Bookings + rewards
    cur.execute(
        """
        SELECT b.booking_id, b.booking_date,
               p.property_id, p.location, p.city, p.state, p.price,
               rw.points_balance
        FROM Rewards rw
        JOIN Booking b ON b.booking_id = rw.booking_id
        JOIN Property p ON p.property_id = b.property_id
        WHERE rw.email = %s
        ORDER BY b.booking_date DESC;
        """,
        (email,),
    )
    bookings = cur.fetchall()

    # Total points
    cur.execute(
        "SELECT COALESCE(SUM(points_balance), 0) AS total_points FROM Rewards WHERE email = %s;",
        (email,),
    )
    total_points = cur.fetchone()["total_points"]

    cur.close()
    conn.close()

    return render_template(
        "renter_dashboard.html",
        renter=renter,
        bookings=bookings,
        total_points=total_points,
    )


if __name__ == "__main__":
    app.run(debug=True)