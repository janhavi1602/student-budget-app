from flask import Flask, render_template, request, redirect, session
import json
import os

app = Flask(__name__)
app.secret_key = "secret123"


# Ensure users.json exists
if not os.path.exists("users.json"):
    with open("users.json", "w") as f:
        json.dump([], f)


# 🔐 LOGIN
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with open("users.json", "r") as f:
            users = json.load(f)

        for user in users:
            if user['username'] == username and user['password'] == password:
                session['user'] = username
                return redirect('/dashboard')

        return render_template('login.html', error="Invalid Username or Password")

    return render_template('login.html')


# 📝 SIGNUP
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with open("users.json", "r") as f:
            users = json.load(f)

        # Check if user already exists
        for user in users:
            if user['username'] == username:
                return render_template('signup.html', error="Username already exists")

        users.append({
            "username": username,
            "password": password
        })

        with open("users.json", "w") as f:
            json.dump(users, f)

        return redirect('/')

    return render_template('signup.html')


# 📊 DASHBOARD
@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('index.html', username=session['user'])
    return redirect('/')


# 🚪 LOGOUT
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


# 🚀 RUN
if __name__ == '__main__':
    app.run(debug=True)
