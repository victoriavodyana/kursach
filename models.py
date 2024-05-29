from config import db
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from sqlalchemy import BigInteger
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timezone



class Warehouses(db.Model):
    warehouse_id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(120), nullable=False)


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('warehouses.warehouse_id'))
    password = db.Column(db.String(320), nullable=False)
    city = db.relationship('Warehouses')

    actions = db.relationship('Items_actions', backref='user_parent', cascade='all, delete-orphan')


class Items(db.Model):
    full_item_id = db.Column(BigInteger, primary_key=True)
    city_id = db.Column(db.Integer, db.ForeignKey('warehouses.warehouse_id'), primary_key=True)
    item_model = db.Column(db.String(80), nullable=False)
    item_model_id = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(80), db.ForeignKey('categories.name', onupdate='CASCADE', ondelete='RESTRICT'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    producing_country = db.Column(db.String(120), nullable=False)
    colour = db.Column(db.String(80), nullable=False)
    manufacturer = db.Column(db.String(80), nullable=False)
    img = db.Column(db.String(255), nullable=True)
    bar_code = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Integer, nullable=True)
    place = db.Column(db.String(80), nullable=True)

    city = db.relationship('Warehouses')
    item_actions = db.relationship('Items_actions', backref='item_parent', cascade='all, delete-orphan')


class Items_departure_temp(db.Model):
    departure_id = db.Column(db.Integer, primary_key=True)
    full_item_id = db.Column(BigInteger, nullable=False)
    city_from_id = db.Column(db.Integer, db.ForeignKey('warehouses.warehouse_id'))
    city_to_id = db.Column(db.Integer, db.ForeignKey('warehouses.warehouse_id'))
    item_model = db.Column(db.String(80), nullable=False)
    item_model_id = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(80), db.ForeignKey('categories.name', onupdate='CASCADE', ondelete='RESTRICT'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    producing_country = db.Column(db.String(120), nullable=False)
    colour = db.Column(db.String(80), nullable=False)
    manufacturer = db.Column(db.String(80), nullable=False)
    img = db.Column(db.String(255), nullable=True)
    bar_code = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Integer, nullable=True)
    place = db.Column(db.String(80), nullable=True)

    city_from = db.relationship('Warehouses', foreign_keys=[city_from_id], backref='departures_from')
    city_to = db.relationship('Warehouses', foreign_keys=[city_to_id], backref='departures_to')

    category_rel = db.relationship('Categories', backref='items_temp', foreign_keys=[category])


class Items_actions(db.Model):
    action_id = db.Column(db.Integer, primary_key=True)
    full_item_id = db.Column(BigInteger, db.ForeignKey('items.full_item_id', ondelete='CASCADE', onupdate='CASCADE'))
    city_id = db.Column(db.Integer, db.ForeignKey('warehouses.warehouse_id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    action = db.Column(db.String(80), nullable=False)
    date_action = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    item = db.relationship('Items', backref='actions', single_parent=True, cascade="save-update, merge, refresh-expire")
    user = db.relationship('Users', backref='user_actions')

class Suppliers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(120), unique=True, nullable=False)
    city = db.Column(db.String(80), nullable=False)

class Customers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(120), unique=True, nullable=False)
    city = db.Column(db.String(80), nullable=False)

class Categories(db.Model):
    name = db.Column(db.String(80), primary_key=True)
    category_img = db.Column(db.String(255), nullable=True)
