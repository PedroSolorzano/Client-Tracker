from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = "ouhsegiu23t93jknfib2398bi2c921038hcv3"
Bootstrap(app)

# CONNECT TO DB
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///blog.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


@app.route('/')
def home_page():
    return render_template('index.html')


@app.route('/billing')
def billing_page():
    return render_template('billing.html')


@app.route('/profile')
def profile_page():
    return render_template('profile.html')


@app.route('/login')
def login_page():
    return render_template('sign-in.html')


@app.route('/register')
def register_page():
    return render_template('sign-up.html')


@app.route('/clients')
def client_page():
    return render_template('clients.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=81, debug=True)
