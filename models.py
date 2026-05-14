from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    account_type = db.Column(db.String(20), default='personal') # 'personal' or 'company'
    company_name = db.Column(db.String(150), nullable=True)
    entries = db.relationship('CarbonEntry', backref='user', lazy=True)

class CarbonEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False) # e.g. "electricity", "transport"
    value = db.Column(db.Float, nullable=False) # The amount, e.g. km or kWh
    unit = db.Column(db.String(20), nullable=False)
    carbon_emission = db.Column(db.Float, nullable=False) # in kg CO2
    date = db.Column(db.DateTime, default=datetime.utcnow)
