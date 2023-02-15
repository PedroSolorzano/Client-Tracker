from flask import Flask, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, fresh_login_required, logout_user
from forms import LoginForm, RegisterForm, UserInformationForm, ClientInformationForm
from flask_gravatar import Gravatar
from functools import wraps
from sqlalchemy import ForeignKey
from flask_bcrypt import Bcrypt
import bcrypt
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
    username = db.Column(db.String(1000), nullable=False)
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
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
@login_required
def home_page():
    return render_template('index.html', logged_in=current_user.is_authenticated)


@app.route('/clients')
@login_required
def client_page():
    return render_template('clients.html', logged_in=current_user.is_authenticated)


@app.route('/billing')
@fresh_login_required
def billing_page():
    return render_template('billing.html', logged_in=current_user.is_authenticated)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile_page():
    user_form = UserInformationForm()
    if request.method == 'POST' and user_form.validate_on_submit() and user_form.submit.data:
        user = User.query.get(current_user.id)
        # Change user's data
        user.username = user_form.username.data
        user.first_name = user_form.first_name.data
        user.last_name = user_form.last_name.data
        user.about_me = user_form.about_me.data
        # for changing the email, it must first be checked that the new email doesn't already exist
        taken_email = User.query.filter(email=user_form.email.data).first()
        if not taken_email:
            user.email = user_form.email.data
            # Commit to database
            db.session.commit()
        else:
            # Commit to database
            db.session.commit()
        return redirect(url_for('profile_page', form=user_form, logged_in=current_user.is_authenticated))
    elif request.method == 'POST' and user_form.cancel.data:
        return redirect(url_for('profile_page', form=user_form, logged_in=current_user.is_authenticated))
    return render_template('profile.html', form=user_form, logged_in=current_user.is_authenticated)


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    login_form = LoginForm()
    register_form = RegisterForm()
    user = User.query.filter_by(email=register_form.email.data).first()
    if request.method == 'POST' and register_form.validate_on_submit() and not user:
        # Bcrypt password (rounds are defaulted to 12)
        bcrypt_pwd = bcrypt.generate_password_hash(register_form.password.data)
        new_user = User(email=register_form.email.data,
                        password=bcrypt_pwd,
                        username=register_form.name.data)
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


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    login_form = LoginForm()
    register_form = RegisterForm()
    if request.method == 'GET':
        return render_template("sign-in.html", form=login_form, logged_in=current_user.is_authenticated)

    if request.method == 'POST' and login_form.validate_on_submit():
        user = User.query.filter_by(email=login_form.email.data).first()

        if not user:
            flash("This email doesn't exist, please register first.")
            return redirect(url_for('register_page', form=register_form, logged_in=current_user.is_authenticated))
        elif current_user.is_active:
            flash('User already logged in.')
            return redirect(url_for('login_page', form=login_form, logged_in=current_user.is_authenticated))
        elif user and bcrypt.check_password_hash(user.password, login_form.password.data):
            # Login user
            login_user(user)
            return redirect(url_for('profile_page', logged_in=current_user.is_authenticated))
        else:
            flash('Incorrect password, please try again.')
            return redirect(url_for('login_page', form=login_form, logged_in=current_user.is_authenticated))


@app.route('/logout')
@login_required
def logout():
    if current_user.is_authenticated:
        logout_user()
        return redirect(url_for('login_page', logged_in=current_user.is_authenticated))
    else:
        return redirect(url_for('login_page', logged_in=current_user.is_authenticated))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=81, debug=True)
