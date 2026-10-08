from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import date

app = Flask(__name__)

DATABASE = "medicine_tracker.db"


# ---------------- DATABASE CONNECTION ----------------

def get_db():

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    connection.executescript("""
    
    CREATE TABLE IF NOT EXISTS Suppliers (
        Supplier_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Supplier_Name TEXT NOT NULL,
        Phone TEXT,
        Email TEXT
    );

    CREATE TABLE IF NOT EXISTS Categories (
        Category_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Category_Name TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS Medicines (
        Medicine_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Medicine_Name TEXT NOT NULL,
        Category_ID INTEGER,
        Supplier_ID INTEGER,
        Batch_No TEXT NOT NULL,
        Quantity INTEGER NOT NULL,
        Price REAL NOT NULL,
        Manufacture_Date TEXT NOT NULL,
        Expiry_Date TEXT NOT NULL,

        FOREIGN KEY (Category_ID)
            REFERENCES Categories(Category_ID),

        FOREIGN KEY (Supplier_ID)
            REFERENCES Suppliers(Supplier_ID)
    );

    CREATE TABLE IF NOT EXISTS Stock_Transactions (
        Transaction_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Medicine_ID INTEGER NOT NULL,
        Transaction_Type TEXT NOT NULL,
        Quantity INTEGER NOT NULL,
        Transaction_Date TEXT NOT NULL,

        FOREIGN KEY (Medicine_ID)
            REFERENCES Medicines(Medicine_ID)
    );

    """)

    connection.commit()

    return connection


# ---------------- HOME PAGE ----------------

@app.route("/")
def index():

    db = get_db()

    medicines = db.execute("""
        SELECT *
        FROM Medicines
        ORDER BY Medicine_ID DESC
    """).fetchall()

    totals = db.execute("""
        SELECT COUNT(*) AS total_medicines,
               COALESCE(SUM(Quantity), 0) AS total_stock
        FROM Medicines
    """).fetchone()
    total_suppliers = db.execute(
        "SELECT COUNT(*) FROM Suppliers"
    ).fetchone()[0]

    db.close()

    today = date.today()
    expired_count = 0
    expiring_soon_count = 0
    dashboard_medicines = []

    for medicine in medicines:
        medicine_data = dict(medicine)
        days_remaining = (
            date.fromisoformat(medicine_data["Expiry_Date"]) - today
        ).days

        if days_remaining < 0:
            medicine_data["expiry_status"] = "Expired"
            medicine_data["status_class"] = "expired"
            expired_count += 1
        elif days_remaining <= 30:
            medicine_data["expiry_status"] = "Expiring Soon"
            medicine_data["status_class"] = "expiring"
            expiring_soon_count += 1
        else:
            medicine_data["expiry_status"] = "Safe"
            medicine_data["status_class"] = "safe"

        dashboard_medicines.append(medicine_data)

    return render_template(
        "index.html",
        medicines=dashboard_medicines,
        total_medicines=totals["total_medicines"],
        total_stock=totals["total_stock"],
        total_suppliers=total_suppliers,
        expired_count=expired_count,
        expiring_soon_count=expiring_soon_count,
        today=today.strftime("%B %d, %Y")
    )


# ---------------- VIEW MEDICINES ----------------

@app.route("/medicines")
def medicines():

    db = get_db()

    medicines = db.execute("""
        SELECT *
        FROM Medicines
        ORDER BY Medicine_ID DESC
    """).fetchall()

    db.close()

    return render_template(
        "medicines.html",
        medicines=medicines
    )


# ---------------- ADD MEDICINE ----------------

@app.route("/add_medicine", methods=["GET", "POST"])
def add_medicine():

    db = get_db()

    if request.method == "POST":

        medicine_name = request.form["medicine_name"]
        category_id = request.form["category_id"]
        supplier_id = request.form["supplier_id"]
        batch_no = request.form["batch_no"]
        quantity = request.form["quantity"]
        price = request.form["price"]
        manufacture_date = request.form["manufacture_date"]
        expiry_date = request.form["expiry_date"]

        db.execute("""
            INSERT INTO Medicines
            (
                Medicine_Name,
                Category_ID,
                Supplier_ID,
                Batch_No,
                Quantity,
                Price,
                Manufacture_Date,
                Expiry_Date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            medicine_name,
            category_id,
            supplier_id,
            batch_no,
            quantity,
            price,
            manufacture_date,
            expiry_date
        ))

        db.commit()
        db.close()

        return redirect(url_for("medicines"))

    categories = db.execute(
        "SELECT * FROM Categories"
    ).fetchall()

    suppliers = db.execute(
        "SELECT * FROM Suppliers"
    ).fetchall()

    db.close()

    return render_template(
        "add_medicine.html",
        categories=categories,
        suppliers=suppliers
    )


# ---------------- EDIT MEDICINE ----------------

@app.route("/edit_medicine/<int:medicine_id>", methods=["GET", "POST"])
def edit_medicine(medicine_id):

    db = get_db()

    if request.method == "POST":

        medicine_name = request.form["medicine_name"]
        category_id = request.form["category_id"]
        supplier_id = request.form["supplier_id"]
        batch_no = request.form["batch_no"]
        quantity = request.form["quantity"]
        price = request.form["price"]
        manufacture_date = request.form["manufacture_date"]
        expiry_date = request.form["expiry_date"]

        db.execute("""
            UPDATE Medicines
            SET
                Medicine_Name = ?,
                Category_ID = ?,
                Supplier_ID = ?,
                Batch_No = ?,
                Quantity = ?,
                Price = ?,
                Manufacture_Date = ?,
                Expiry_Date = ?
            WHERE Medicine_ID = ?
        """, (
            medicine_name,
            category_id,
            supplier_id,
            batch_no,
            quantity,
            price,
            manufacture_date,
            expiry_date,
            medicine_id
        ))

        db.commit()
        db.close()

        return redirect(url_for("medicines"))

    medicine = db.execute("""
        SELECT *
        FROM Medicines
        WHERE Medicine_ID = ?
    """, (medicine_id,)).fetchone()

    categories = db.execute(
        "SELECT * FROM Categories"
    ).fetchall()

    suppliers = db.execute(
        "SELECT * FROM Suppliers"
    ).fetchall()

    db.close()

    return render_template(
        "edit_medicine.html",
        medicine=medicine,
        categories=categories,
        suppliers=suppliers
    )


# ---------------- DELETE MEDICINE ----------------

@app.route("/delete_medicine/<int:medicine_id>")
def delete_medicine(medicine_id):

    db = get_db()

    db.execute("""
        DELETE FROM Medicines
        WHERE Medicine_ID = ?
    """, (medicine_id,))

    db.commit()
    db.close()

    return redirect(url_for("medicines"))


# ---------------- ADD SUPPLIER ----------------

@app.route("/add_supplier", methods=["GET", "POST"])
def add_supplier():

    if request.method == "POST":

        supplier_name = request.form["supplier_name"]
        phone = request.form["phone"]
        email = request.form["email"]

        db = get_db()

        db.execute("""
            INSERT INTO Suppliers
            (Supplier_Name, Phone, Email)
            VALUES (?, ?, ?)
        """, (
            supplier_name,
            phone,
            email
        ))

        db.commit()
        db.close()

        return redirect(url_for("index"))

    return render_template("add_supplier.html")


# ---------------- ADD PURCHASE ----------------

@app.route("/add_purchase", methods=["GET", "POST"])
def add_purchase():

    db = get_db()

    if request.method == "POST":

        medicine_id = request.form["medicine_id"]
        quantity = int(request.form["quantity"])

        db.execute("""
            UPDATE Medicines
            SET Quantity = Quantity + ?
            WHERE Medicine_ID = ?
        """, (
            quantity,
            medicine_id
        ))

        db.execute("""
            INSERT INTO Stock_Transactions
            (
                Medicine_ID,
                Transaction_Type,
                Quantity,
                Transaction_Date
            )
            VALUES (?, ?, ?, ?)
        """, (
            medicine_id,
            "IN",
            quantity,
            date.today().isoformat()
        ))

        db.commit()
        db.close()

        return redirect(url_for("purchases"))

    medicines = db.execute("""
        SELECT *
        FROM Medicines
    """).fetchall()

    db.close()

    return render_template(
        "add_purchase.html",
        medicines=medicines
    )


# ---------------- PURCHASES ----------------

@app.route("/purchases")
def purchases():

    db = get_db()

    purchases = db.execute("""
        SELECT
            Stock_Transactions.Transaction_ID,
            Medicines.Medicine_Name,
            Stock_Transactions.Transaction_Type,
            Stock_Transactions.Quantity,
            Stock_Transactions.Transaction_Date
        FROM Stock_Transactions
        JOIN Medicines
        ON Stock_Transactions.Medicine_ID =
           Medicines.Medicine_ID
        ORDER BY Stock_Transactions.Transaction_ID DESC
    """).fetchall()

    db.close()

    return render_template(
        "purchases.html",
        purchases=purchases
    )


# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":
    app.run(debug=True)