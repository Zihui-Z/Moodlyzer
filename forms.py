from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    role = SelectField('Role', choices=[('patient', 'Patient'), ('doctor', 'Doctor')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# log
from flask_wtf import FlaskForm
from wtforms import TextAreaField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class MoodLogForm(FlaskForm):
    text_entry = TextAreaField('How are you feeling today?', validators=[DataRequired()])
    mood_score = IntegerField('Mood Score (1-10)', validators=[DataRequired(), NumberRange(min=1, max=10)])
    submit = SubmitField('Submit Mood')