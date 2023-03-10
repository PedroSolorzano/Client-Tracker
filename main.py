from flask import Flask, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, Session
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, fresh_login_required, \
    logout_user
from forms import LoginForm, RegisterForm, UserInformationForm, ClientInformationForm
from flask_gravatar import Gravatar
from functools import wraps
from sqlalchemy import ForeignKey, create_engine
from flask_bcrypt import Bcrypt
import time
import os

# CONSTANTS
login_duration = timedelta(minutes=5)

# Flask app and bootstrap
app = Flask(__name__)
app.config['SECRET_KEY'] = "ouhsegiu23t93jknfib2398bi2c921038hcv3"
Bootstrap(app)

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_page'

# CONNECT TO DB
app.app_context().push()
engine = create_engine("sqlite:///instance/client-tracker.db")
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///client-tracker.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Bcrypt
bcrypt = Bcrypt(app)


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
    partners = relationship("Partner", back_populates="user")


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


class Partner(db.Model):
    __tablename__ = "partners"
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
    user = relationship("User", back_populates="partners")
    notifications = relationship("Notification", back_populates="partner")
    comments = relationship("Comment", back_populates="partner")


class Notification(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, ForeignKey("clients.id"))
    partner_id = db.Column(db.Integer, ForeignKey("partners.id"))
    date_created = db.Column(db.DateTime, nullable=False)
    date_to_notify = db.Column(db.DateTime, nullable=False)
    text = db.Column(db.String(3000), nullable=False)
    # Relationships
    client = relationship("Client", back_populates="notifications")
    partner = relationship("Partner", back_populates="notifications")


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, ForeignKey("clients.id"))
    partner_id = db.Column(db.Integer, ForeignKey("partners.id"))
    date_created = db.Column(db.DateTime, nullable=False)
    text = db.Column(db.String(3000), nullable=False)
    # Relationships
    client = relationship("Client", back_populates="comments")
    partner = relationship("Partner", back_populates="comments")


db.create_all()


# LoginManager
@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(user_id)
    return user


# Logout user if they lose auth by closing the browser, or other instances
@app.before_request
def check_auth():
    if not current_user.is_authenticated:
        # log the user out
        logout_user()


@app.route('/')
@login_required
def home_page():
    return render_template('index.html',
                           logged_in=current_user.is_authenticated)


@app.route('/clients')
@login_required
def client_page():
    return render_template('clients.html',
                           logged_in=current_user.is_authenticated)


@app.route('/billing')
@fresh_login_required
def billing_page():
    return render_template('billing.html',
                           logged_in=current_user.is_authenticated)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile_page():
    user_form = UserInformationForm(
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        username=current_user.username,
        email=current_user.email,
        about_me=current_user.about_me
    )
    user = User.query.get(current_user.id)
    if request.method == 'POST' and user_form.submit.data:
        with Session(engine) as session:
            session.begin()
            # Change user's data
            user.username = user_form.username.data
            user.first_name = user_form.first_name.data
            user.last_name = user_form.last_name.data
            user.about_me = user_form.about_me.data
            # for changing the email, it must first be checked that the new email doesn't already exist
            taken_email = User.query.filter_by(email=user_form.email.data).first()
            if not taken_email:
                user.email = user_form.email.data
            # Commit to database
            session.commit()
            print(current_user.email)
        return redirect(url_for('profile_page', form=user_form, logged_in=current_user.is_authenticated))
    elif request.method == 'POST' and user_form.cancel.data:
        print(current_user.username)
        return redirect(url_for('profile_page', form=user_form, logged_in=current_user.is_authenticated))
    print(current_user.id)
    return render_template('profile.html', form=user_form, logged_in=current_user.is_authenticated)


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    login_form = LoginForm()
    register_form = RegisterForm()
    user = User.query.filter_by(email=register_form.email.data).first()
    if request.method == 'POST' and register_form.validate_on_submit() and not user:
        # bcrypt password
        bcrypt_pwd = bcrypt.generate_password_hash(
            register_form.password.data)
        new_user = User(email=register_form.email.data,
                        password=bcrypt_pwd,
                        username=register_form.username.data)
        with Session(engine) as session:
            session.add(new_user)
            session.commit()
            # Login user
            login_user(user, duration=login_duration)
        return redirect(
            url_for('profile_page', logged_in=current_user.is_authenticated))
    elif request.method == 'POST' and register_form.validate_on_submit() and user:
        flash('That user already exists, log in instead!')
        return redirect(
            url_for('login_page',
                    form=login_form,
                    logged_in=current_user.is_authenticated))
    else:
        return render_template('sign-up.html',
                               form=register_form,
                               logged_in=current_user.is_authenticated)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    login_form = LoginForm()
    register_form = RegisterForm()
    if request.method == 'GET':
        return render_template("sign-in.html",
                               form=login_form,
                               logged_in=current_user.is_authenticated)

    if request.method == 'POST' and login_form.validate_on_submit():
        user = User.query.filter_by(email=login_form.email.data).first()

        if not user:
            flash("This email doesn't exist, please register first.")
            return redirect(
                url_for('register_page',
                        form=register_form,
                        logged_in=current_user.is_authenticated))
        elif current_user.is_active:
            flash('User already logged in.')
            return redirect(
                url_for('login_page',
                        form=login_form,
                        logged_in=current_user.is_authenticated))
        elif user and bcrypt.check_password_hash(user.password, login_form.password.data):
            # Login user
            with Session(engine) as session:
                session.begin()
                login_user(user, duration=login_duration)
            return redirect(
                url_for('profile_page', logged_in=current_user.is_authenticated))
        else:
            flash('Incorrect password, please try again.')
            return redirect(
                url_for('login_page',
                        form=login_form,
                        logged_in=current_user.is_authenticated))


@app.route('/logout')
@login_required
def logout():
    if current_user.is_authenticated:
        logout_user()
        return redirect(
            url_for('login_page', logged_in=current_user.is_authenticated))
    else:
        return redirect(
            url_for('login_page', logged_in=current_user.is_authenticated))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=81, debug=True)
