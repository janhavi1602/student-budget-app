from flask import Flask, render_template, request, redirect, session
import json, os

app = Flask(__name__)
app.secret_key = "secret123"

# Create files if not exist
if not os.path.exists("users.json"):
    with open("users.json", "w") as f:
        json.dump([], f)

if not os.path.exists("data.json"):
    with open("data.json", "w") as f:
        json.dump({}, f)


# LOGIN
@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users = json.load(open("users.json"))

        for user in users:
            if user['username'] == username and user['password'] == password:
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

        users = json.load(open("users.json"))

        for user in users:
            if user['username'] == username:
                return render_template('signup.html', error="Username already exists")

        users.append({"username": username, "password": password})
        json.dump(users, open("users.json", "w"))

        return redirect('/')

    return render_template('signup.html')


# DASHBOARD
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')

    username = session['user']
    data = json.load(open("data.json"))

    user_data = data.get(username, {"income": 0, "expenses": []})

    total_expense = sum(item["amount"] for item in user_data["expenses"])
    balance = user_data["income"] - total_expense

    return render_template(
        'index.html',
        username=username,
        income=user_data["income"],
        expenses=user_data["expenses"],
        total_expense=total_expense,
        balance=balance
    )


# ADD INCOME
@app.route('/add_income', methods=['POST'])
def add_income():
    username = session['user']
    amount = int(request.form['amount'])

    data = json.load(open("data.json"))

    if username not in data:
        data[username] = {"income": 0, "expenses": []}

    data[username]["income"] += amount

    json.dump(data, open("data.json", "w"))

    return redirect('/dashboard')


# ADD EXPENSE
@app.route('/add_expense', methods=['POST'])
def add_expense():
    username = session['user']
    category = request.form['category']
    amount = int(request.form['amount'])

    data = json.load(open("data.json"))

    if username not in data:
        data[username] = {"income": 0, "expenses": []}

    data[username]["expenses"].append({
        "category": category,
        "amount": amount
    })

    json.dump(data, open("data.json", "w"))

    return redirect('/dashboard')


# DELETE EXPENSE
@app.route('/delete/<int:index>')
def delete(index):
    username = session['user']
    data = json.load(open("data.json"))

    if username in data:
        data[username]["expenses"].pop(index)

    json.dump(data, open("data.json", "w"))

    return redirect('/dashboard')


# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
