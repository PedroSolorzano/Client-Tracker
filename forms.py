from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField
from wtforms.validators import DataRequired


# WTForms
class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign up")


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log in")


class UserInformationForm(FlaskForm):
    first_name = StringField("First Name")
    last_name = StringField("Last Name")
    username = StringField("Username", validators=[DataRequired()])
    email = EmailField("Email address", validators=[DataRequired()])
    about_me = StringField("About Me")
    submit = SubmitField('Submit Changes')
    cancel = SubmitField('Cancel')


class ClientInformationForm(FlaskForm):
    first_name = StringField("First Name")
    last_name = StringField("Last Name")
    username = StringField("Username", validators=[DataRequired()])
    email = EmailField("Email address", validators=[DataRequired()])
    address = StringField("Address")
    city = StringField("City")
    country = StringField("Country")
    postal_code = StringField("Postal Code")
    about_me = StringField("About Me")
    submit = SubmitField('Submit Changes')
    cancel = SubmitField('Cancel')

