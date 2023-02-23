from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, DateField
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
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    email = EmailField("Email address", validators=[DataRequired()])
    about_me = StringField("About Me", validators=[DataRequired()])
    submit = SubmitField('Submit Changes', validators=[DataRequired()])
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
    birthday = DateField("Birthday")
    Ocupation = StringField("Ocupation")
    about_me = StringField("About Me")
    submit = SubmitField('Submit Changes')
    cancel = SubmitField('Cancel')


class PartnerInformationForm(FlaskForm):
    first_name = StringField("First Name")
    last_name = StringField("Last Name")
    username = StringField("Username", validators=[DataRequired()])
    email = EmailField("Email address", validators=[DataRequired()])
    address = StringField("Address")
    city = StringField("City")
    country = StringField("Country")
    postal_code = StringField("Postal Code")
    birthday = DateField("Birthday")
    Ocupation = StringField("Ocupation")
    about_me = StringField("About Me")
    submit = SubmitField('Submit Changes')
    cancel = SubmitField('Cancel')
