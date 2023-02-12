from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import LoginForm, RegisterForm
from flask_gravatar import Gravatar
from functools import wraps
from sqlalchemy import ForeignKey
from flask_bcrypt import Bcrypt
import os

# Flask app and bootstrap
app = Flask(__name__)
app.config['SECRET_KEY'] = "ouhsegiu23t93jknfib2398bi2c921038hcv3"
Bootstrap(app)


# CONNECT TO DB
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///client-tracker.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Bcrypt
bcrypt = Bcrypt(app)


# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_page'


# CONFIGURE TABLES
class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(1000), nullable=False)
    about_me = db.Column(db.String(1000), nullable=True)
    # Relationships
    clients = relationship("Client", back_populates="user")


class Client(db.Model):
    __tablename__ = "clients"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("users.id"))
    email = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(1000), nullable=False)
    address = db.Column(db.String(1000), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    postal_code = db.Column(db.Integer, nullable=True)
    birthday = db.Column(db.DateTime, nullable=True)
    occupation = db.Column(db.String(1000), nullable=True)
    # Relationships
    user = relationship("User", back_populates="clients")
    notifications = relationship("Notification", back_populates="client")
    comments = relationship("Comment", back_populates="client")


class Notification(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, ForeignKey("clients.id"))
    date_created = db.Column(db.DateTime, nullable=False)
    date_to_notify = db.Column(db.DateTime, nullable=False)
    text = db.Column(db.String(3000), nullable=False)
    # Relationships
    client = relationship("Client", back_populates="notifications")


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, ForeignKey("clients.id"))
    date_created = db.Column(db.DateTime, nullable=False)
    text = db.Column(db.String(3000), nullable=False)
    # Relationships
    client = relationship("Client", back_populates="comments")


db.create_all()


# LoginManager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/')
def home_page():
    return render_template('index.html')


@app.route('/billing')
def billing_page():
    return render_template('billing.html')


@app.route('/profile')
@login_required
def profile_page():
    return render_template('profile.html')


@app.route('/login')
def login_page():
    return render_template('sign-in.html')


@app.route('/logout')
def logout():
    return render_template('sign-in.html')


@app.route('/register', methods=['POST', 'GET'])
def register_page():
    login_form = LoginForm()
    register_form = RegisterForm()
    user = User.query.filter_by(email=register_form.email.data).first()
    if request.method == 'POST' and register_form.validate_on_submit() and not user:
        # Bcrypt password (rounds are defaulted to 12)
        bcrypt_pwd = bcrypt.generate_password_hash(register_form.password.data)
        new_user = User(email=register_form.email.data,
                        password=bcrypt_pwd,
                        name=register_form.name.data)
        db.session.add(new_user)
        db.session.commit()
        # Login user
        login_user(new_user)
        return redirect(url_for('profile_page', logged_in=current_user.is_authenticated))
    elif request.method == 'POST' and register_form.validate_on_submit() and user:
        flash('That user already exists, log in instead!')
        return redirect(url_for('login_page', form=login_form, logged_in=current_user.is_authenticated))
    else:
        return render_template('sign-up.html', form=register_form, logged_in=current_user.is_authenticated)


@app.route('/clients')
def client_page():
    return render_template('clients.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=81, debug=True)
