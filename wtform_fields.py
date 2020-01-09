from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FloatField, IntegerField
from wtforms.validators import InputRequired, Email, Length, EqualTo, ValidationError, Optional

class RegistartionForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(message='Username Required')])
    email = StringField('email', validators=[InputRequired(message='email Required'), Email(message="This field requires a valid email address")])
    password = PasswordField('password', validators=[InputRequired(message="Password Required")])
    confirm_pswd = PasswordField("confirm_pswd", validators=[InputRequired(message="Confirm Password Required"), EqualTo('password', message='Password must match')])
