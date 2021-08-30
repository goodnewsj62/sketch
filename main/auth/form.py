from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired,Length,Email,EqualTo,ValidationError
from flask_login import current_user

from ..database import Database
from ..models import User,Post,Notification,follow
from .. import bcrypt_

db = Database(User,Post,Notification,follow)

class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(),Length(min=2,max=50)])
    password = PasswordField('password', validators=[DataRequired(), Length(min=7,max=30)]) 
    remember = BooleanField('remember')

    def validate_username(self, username):
        if not db.get_user_by_username(username) or not db.get_user_by_email(username):
            raise ValidationError('Incorrect username or password')


class RegisterForm(FlaskForm):
    name = StringField('name', validators=[DataRequired(),Length(min=3,max=50)])
    username = StringField('username', validators=[DataRequired(),Length(min=3,max=30)])
    email =  StringField('email', validators=[DataRequired(),Length(min=5,max=50),Email()])
    contact = StringField('phone',validators=[Length(min=5,max=15)])
    password = PasswordField('password',validators=[DataRequired(), Length(min=7,max=30)])
    confirm_p = PasswordField('password',validators=[DataRequired(), Length(min=7,max=30),EqualTo('password')])

    def validate_username(self,username):
        if db.get_user_by_username(username):
            raise ValidationError('username already exist')
    
    def validate_email(self,email):
        if len(email) == 0:
            raise ValidationError('please enter an email')
        if db.get_user_by_email(email):
            raise ValidationError('email already exist')
    
class ChangePassword(FlaskForm):
    old_password = PasswordField("current password",validators=[DataRequired()]) 
    password = PasswordField('password',validators=[DataRequired(), Length(min=7,max=30)])
    confirm_p = PasswordField('password',validators=[DataRequired(), Length(min=7,max=30),EqualTo('password')])

    def validate_old_password(self,old_password):
        user = db.get_user_by_username(current_user.username)
        if not bcrypt_.check_password_hash(user.password,old_password):
            raise ValidationError("Invalid current password")