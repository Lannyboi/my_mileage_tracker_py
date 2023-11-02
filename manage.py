from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    hash = db.Column(db.String(255), nullable=False)
    cars = db.relationship('Car', backref='user', lazy=True)

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    car_year = db.Column(db.Integer, nullable=False)
    make = db.Column(db.String(80), nullable=False)
    model = db.Column(db.String(80), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    fuel_info = db.relationship('FuelInfo', backref='car', lazy=True)

class FuelInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    day = db.Column(db.Integer, nullable=False)
    total_miles = db.Column(db.Float, nullable=False)
    price_per_gallon = db.Column(db.Float, nullable=False)
    total_gallons = db.Column(db.Float, nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=True)
