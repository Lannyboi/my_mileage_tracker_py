from flask import Flask, redirect, render_template, request, session, jsonify
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import login_required, usd

app = Flask(__name__)
app.jinja_env.filters["usd"] = usd

app.config['SECRET_KEY'] = 'the friends we made along the way'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://lvyoumqzneedyl:21cd8831f240f60715dfaf722f3508b97bbcd7d3205836cbe371ceec2fbde3c3@ec2-3-230-24-12.compute-1.amazonaws.com:5432/dbvf8fu77agh8h"
Session(app)

db = SQLAlchemy(app)

# Classes
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    hash = db.Column(db.String, nullable=False)

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    car_year = db.Column(db.Integer, nullable=False)
    make = db.Column(db.String, nullable=False)
    model = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='cars')

class FuelInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    day = db.Column(db.Integer, nullable=False)
    total_miles = db.Column(db.Float, nullable=False)
    price_per_gallon = db.Column(db.Float, nullable=False)
    total_gallons = db.Column(db.Float, nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'))
    car = db.relationship('Car', backref='fuel_info')


""" app routes """
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


@app.route("/add-car", methods=["GET", "POST"])
@login_required
def addCar():
    # If GET, render addCar page
    if request.method == "GET":
        return render_template("addCar.html")
    
    # If POST, try to add car
    elif request.method == "POST":
        year = int(request.form.get("year"))
        make = request.form.get("make")
        model = request.form.get("model")

        if not year or not make or not model:
            return "Please fill out all required fields"
        else:
            print(year, make, model, session["user_id"])
            db.execute("INSERT INTO cars (car_year, make, model, user_id) VALUES (?, ?, ?, ?)", year, make, model, session["user_id"])
            return redirect("/")
        

@app.route("/remove-car", methods=["GET", "POST"])
@login_required
def removeCar():
        # If GET, render remove car page
        if request.method == "GET":
            cars = db.execute("SELECT * FROM cars WHERE user_id = ?", session["user_id"])
            return render_template("removeCar.html", cars=cars)
        
        # If POST, try to remove car
        elif request.method == "POST":
            car_id = request.form.get("car-select")
            db.execute("DELETE FROM fuel_info WHERE car_id = ?", car_id)
            db.execute("DELETE FROM cars WHERE id = ?", car_id)
            return redirect("/")
        

@app.route("/add-record", methods=["GET", "POST"])
@login_required
def addRecord():
    cars = db.execute("SELECT * FROM cars WHERE user_id = ?", session["user_id"])
    # If GET, render addRecord page
    if request.method == "GET":
        return render_template("addRecord.html", cars=cars)
    
    elif request.method == "POST":
        # Form values
        car_id = request.form.get("car-select")
        date = request.form.get("date")
        odometer = request.form.get("odometer")
        pricePerGallon = request.form.get("price_per_gallon")
        totalGallons = request.form.get("total_gallons")
        
        # Check that all fields were filled
        if not car_id or not date or not odometer or not pricePerGallon or not totalGallons:
            return "Please provide all information"
        else:
            # Parse the date into year, month, and day
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            year = date_obj.year
            month = date_obj.month
            day = date_obj.day

            # Add record to db and redirect to stats page
            db.execute("INSERT INTO fuel_info (year, month, day, total_miles, price_per_gallon, total_gallons, car_id) VALUES (?, ?, ?, ?, ?, ?, ?)", year, month, day, odometer, pricePerGallon, totalGallons, car_id)
            return redirect("/")
        

@app.route("/view-stats", methods=["GET", "POST"])
@login_required
def viewStats():
    if request.method == "GET":
        cars = db.execute("SELECT * FROM cars WHERE user_id = ?", session["user_id"])
        return render_template("viewStats.html", cars=cars)
    
    elif request.method == "POST":
        car_id = request.form.get("car-select")
        allEntries = db.execute("SELECT fuel_info.* FROM fuel_info JOIN cars on fuel_info.car_id = cars.id WHERE cars.user_id = ? AND cars.id = ?", session["user_id"], car_id)
        return render_template("carStats.html", allEntries=allEntries, car=db.execute("SELECT * FROM cars WHERE id = ?", car_id)[0])
    