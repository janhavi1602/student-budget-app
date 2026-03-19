from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)

# Create users file if it does not exist
if not os.path.exists("users.json"):
    with open("users.json", "w") as file:
        json.dump([], file)


# LOGIN PAGE
@app.route('/signup', methods=['GET','POST'])
def signup():
    return render_template('signup.html')

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        with open('users.json', 'r') as file:
            users = json.load(file)

        for user in users:
            if user['username'] == username and user['password'] == password:
                return redirect('/dashboard')

        return "Invalid Username or Password"

    return render_template('login.html')


# SIGNUP PAGE
@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        with open('users.json', 'r') as file:
            users = json.load(file)

        users.append({
            "username": username,
            "password": password
        })

        with open('users.json', 'w') as file:
            json.dump(users, file)

        return redirect(url_for('login'))

    return render_template('signup.html')


# DASHBOARD PAGE
@app.route('/dashboard')
def dashboard():
    return render_template('index.html')


# RUN APP
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
