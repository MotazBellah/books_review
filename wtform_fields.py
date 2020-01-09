from flask_wtf import FlaskForm
from passlib.hash import pbkdf2_sha256
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FloatField, IntegerField
from wtforms.validators import InputRequired, Email, Length, EqualTo, ValidationError, Optional
from app import db


def email_exists(form, field):
    email = field.data
    user_object = db.execute("SELECT * FROM users WHERE email = :email", {"email": email}).fetchone()
    if user_object:
        raise ValidationError("This email is already exists")


class RegistartionForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(message='Username Required')])
    email = StringField('email', validators=[InputRequired(message='email Required'), Email(message="This field requires a valid email address"), email_exists])
    password = PasswordField('password', validators=[InputRequired(message="Password Required")])
    confirm_pswd = PasswordField("confirm_pswd", validators=[InputRequired(message="Confirm Password Required"), EqualTo('password', message='Password must match')])


class LoginForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(message='email Required'), Email(message="This field requires a valid email address")])
    password = PasswordField('password', validators=[InputRequired(message="Password Required")])
