from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from database.models import User
from database.db_connection import session_maker


class SignInForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign In')


class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_repeat = PasswordField('Repeat password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        session = session_maker()
        user = session.query(User).filter(User.username == username.data).first()
        if user is not None:
            raise ValidationError('User with such name already exists.')


class SendPhotoForm(FlaskForm):
    photo = FileField(validators=[FileRequired(u'file empty'), FileAllowed(['jpg', 'png'], 'Imagaes only')])
    submit = SubmitField()
