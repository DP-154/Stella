from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from database.models import User
from database.queries import get_or_none
from database.db_connection import session_maker


class SignInForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('remember me')
    submit = SubmitField('submit')


class SignUpForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    password_repeat = PasswordField('repeat password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('register')

    def validate_user(self, username):
        session = session_maker()
        user = session.query(User).filter(User.username == username).first()
        if user is not None:
            raise ValidationError('User with such name already exists.')