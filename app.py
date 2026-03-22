from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secret123"

DB = "database.db"

# CREATE TABLES
def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        category TEXT,
        amount INTEGER,
        month TEXT,
        date TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS income (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        amount INTEGER
    )
    """)

    conn.commit()
    conn.close()

init_db()


# LOGIN
@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cur.fetchone()

        conn.close()

        if user:
            session['user'] = username
            return redirect('/dashboard')

        return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')


# SIGNUP
@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        try:
            cur.execute("INSERT INTO users (username,password) VALUES (?,?)", (username,password))
            conn.commit()
        except:
            return render_template('signup.html', error="Username already exists")

        conn.close()
        return redirect('/')

    return render_template('signup.html')


# DASHBOARD
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')

    username = session['user']

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # income
    cur.execute("SELECT SUM(amount) FROM income WHERE username=?", (username,))
    income = cur.fetchone()[0] or 0

    # expenses
    cur.execute("SELECT category, amount, month, date FROM expenses WHERE username=?", (username,))
    rows = cur.fetchall()

    expenses = []
    total_expense = 0

    for row in rows:
        expenses.append({
            "category": row[0],
            "amount": row[1],
            "month": row[2],
            "date": row[3]
        })
        total_expense += row[1]

    balance = income - total_expense

    conn.close()

    return render_template(
        'index.html',
        username=username,
        income=income,
        expenses=expenses,
        total_expense=total_expense,
        balance=balance
    )


# ADD INCOME
@app.route('/add_income', methods=['POST'])
def add_income():
    username = session['user']
    amount = int(request.form['amount'])

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("INSERT INTO income (username, amount) VALUES (?,?)", (username, amount))

    conn.commit()
    conn.close()

    return redirect('/dashboard')


# ADD EXPENSE
@app.route('/add_expense', methods=['POST'])
def add_expense():
    username = session['user']
    category = request.form['category']
    amount = int(request.form['amount'])
    month = request.form['month']
    date = request.form['date']

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO expenses (username, category, amount, month, date)
        VALUES (?,?,?,?,?)
    """, (username, category, amount, month, date))

    conn.commit()
    conn.close()

    return redirect('/dashboard')


# DELETE EXPENSE
@app.route('/delete/<int:index>')
def delete(index):
    username = session['user']

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("DELETE FROM expenses WHERE id=?", (index,))
    conn.commit()

    conn.close()

    return redirect('/dashboard')


# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
