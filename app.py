from flask import Flask, render_template, request, redirect, session
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

DATA_FILE = "data.json"

# ----------------------------
# Load Data
# ----------------------------
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"transactions": [], "monthly_limit": 0}
    with open(DATA_FILE, "r") as file:
        return json.load(file)

# ----------------------------
# Save Data
# ----------------------------
def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# ----------------------------
# Login
# ----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "1234":
            session["user"] = username
            return redirect("/")
        else:
            return render_template("login.html", error="Invalid Credentials")

    return render_template("login.html")

# ----------------------------
# Logout
# ----------------------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

# ----------------------------
# Dashboard
# ----------------------------
@app.route("/")
def index():
    if "user" not in session:
        return redirect("/login")

    data = load_data()
    transactions = data["transactions"]
    monthly_limit = data.get("monthly_limit", 0)

    total_income = sum(t["amount"] for t in transactions if t["type"] == "income")
    total_expense = sum(t["amount"] for t in transactions if t["type"] == "expense")
    balance = total_income - total_expense

    current_month = datetime.now().strftime("%B %Y")

    monthly_expense = sum(
        t["amount"] for t in transactions
        if t["type"] == "expense" and t["month"] == current_month
    )

    percentage = 0
    if monthly_limit > 0:
        percentage = (monthly_expense / monthly_limit) * 100

    category_totals = {}
    for t in transactions:
        if t["type"] == "expense" and t["month"] == current_month:
            category_totals[t["category"]] = category_totals.get(t["category"], 0) + t["amount"]

    return render_template("index.html",
                           transactions=transactions,
                           balance=balance,
                           total_income=total_income,
                           total_expense=total_expense,
                           monthly_expense=monthly_expense,
                           monthly_limit=monthly_limit,
                           percentage=percentage,
                           category_totals=category_totals)

# ----------------------------
# Add Transaction
# ----------------------------
@app.route("/add", methods=["POST"])
def add():
    if "user" not in session:
        return redirect("/login")

    data = load_data()

    transaction = {
        "type": request.form.get("type"),
        "category": request.form.get("category"),
        "description": request.form.get("description"),
        "amount": float(request.form.get("amount")),
        "month": datetime.now().strftime("%B %Y")
    }

    data["transactions"].append(transaction)
    save_data(data)

    return redirect("/")

# ----------------------------
# Delete
# ----------------------------
@app.route("/delete/<int:index>")
def delete(index):
    if "user" not in session:
        return redirect("/login")

    data = load_data()
    if 0 <= index < len(data["transactions"]):
        data["transactions"].pop(index)
        save_data(data)

    return redirect("/")

# ----------------------------
# Set Monthly Limit
# ----------------------------
@app.route("/set_limit", methods=["POST"])
def set_limit():
    if "user" not in session:
        return redirect("/login")

    data = load_data()
    data["monthly_limit"] = float(request.form.get("limit"))
    save_data(data)

    return redirect("/")

# ----------------------------
# Monthly History
# ----------------------------
@app.route("/history")
def history():
    if "user" not in session:
        return redirect("/login")

    data = load_data()
    transactions = data["transactions"]

    monthly_data = {}

    for t in transactions:
        if t["type"] == "expense":
            month = t["month"]
            monthly_data[month] = monthly_data.get(month, 0) + t["amount"]

    return render_template("history.html", monthly_data=monthly_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)