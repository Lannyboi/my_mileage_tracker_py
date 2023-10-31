from cs50 import SQL
from flask import Flask, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

app = Flask(__name__)

app.config['SECRET_KEY'] = 'the friends we made along the way'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///mileageTracker.db")


@app.route("/")
@login_required
def home():
    return render_template("index.html", cars=db.execute("SELECT cars.* FROM cars JOIN users on cars.user_id = users.id WHERE users.id = ?", session["user_id"]))


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    username = request.form.get("username")
    password = request.form.get("password")
    confirmation = request.form.get("confirmation")

    # If GET, render register form
    if request.method == "GET":
        session.clear()
        return render_template("register.html")
    
    # If POST, try to register
    elif request.method == "POST":
        if not username or not password or not confirmation:
            return "Please fill out all required fields"
        elif db.execute("SELECT * FROM USERS WHERE USERNAME = ?", (username)):
            return "Username is already taken"
        elif not (password == confirmation):
            return "Passwords do not match"
        else:
            db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, generate_password_hash(password))
            user_id = db.execute("SELECT id FROM users WHERE username = ?", (username))
            session["user_id"] = user_id[0]["id"]
            return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    # Clear any previous sessions
    session.clear()

    # If POST, try to log in
    if request.method == "POST":
        """ Login function here """
        if not request.form.get("username"):
            return "Must provide username"
        elif not request.form.get("password"):
            return ("Must provide password")
        
        # Check credentials
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return "Invalid username and/or password"
        
        session["user_id"] = rows[0]["id"]
        print(session["user_id"])
        return redirect("/")
    
    # If GET, render login form
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    # Logout
    session.clear()
    return redirect("/")