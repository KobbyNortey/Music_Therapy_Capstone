from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class PlaylistForm(FlaskForm):
    mood = SelectField('How are you feeling right now?', choices=[('tired', 'Tired'), ('stressed', 'Stressed'), ('okay', 'Okay')], validators=[DataRequired()])
    goal = SelectField('What do you want to achieve?', choices=[('relaxation', 'Relaxation'), ('focus', 'Focus'), ('energy', 'Energy')], validators=[DataRequired()])
    submit = SubmitField('Create Playlist')