from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired,Length,Email,EqualTo,ValidationError
from flask_login import current_user

from ..models import User,Post,Notification,follow
from .. import bcrypt_


class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(),Length(min=2,max=50)])
    password = PasswordField('password', validators=[DataRequired(), Length(min=7,max=30)]) 
    remember = BooleanField('remember')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        email = User.query.filter_by(email=username.data).first()
        if not (user or email):
            raise ValidationError('Incorrect username/email or password')


class RegisterForm(FlaskForm):
    name = StringField('name', validators=[DataRequired(),Length(min=3,max=50)])
    username = StringField('username', validators=[DataRequired(),Length(min=3,max=30)])
    email =  StringField('email', validators=[DataRequired(),Length(min=5,max=50),Email()])
    password = PasswordField('password',validators=[DataRequired(), Length(min=7)])
    confirm_p = PasswordField('password',validators=[DataRequired(), Length(min=7),EqualTo('password')])

    def validate_username(self, username):
        if User.query.filter_by(username = username.data).first():
            raise ValidationError('username already exist')
    
    def validate_email(self,email):
        if len(email.data) == 0:
            raise ValidationError('please enter an email')
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('email already exist')

    # def validate_phone_no(self,phone_no):
    #     #if user input phone number then check if its less than five
    #     if phone_no != '':
    #         if len(phone_no) < 5:
    #             raise ValidationError('Invalid phone number')
    
    def validate_password(self,password):
        if password.data == None:
            raise ValidationError('no password input')
        
        if len(password.data) < 7:
            raise ValidationError('password must be up to 7 characters long')

        if not any(n.isupper() for n in password.data):
            raise ValidationError('password must contain capital letter')

        if not any(n.isdigit() for n in password.data):
            raise ValidationError('password must contain a number')


    
class ChangePassword(FlaskForm):
    old_password = PasswordField("current password",validators=[DataRequired()]) 
    password = PasswordField('password',validators=[DataRequired(), Length(min=7,max=30)])
    confirm_p = PasswordField('password',validators=[DataRequired(), Length(min=7,max=30),EqualTo('password')])

    def validate_old_password(self,old_password):
        user = User.query.filter_by(username= current_user.username).first()
        if not bcrypt_.check_password_hash(user.password,old_password.data):
            raise ValidationError("Invalid current password")
    
    def validate_password(self,password):
        if password.data == None:
            raise ValidationError('no password input')
        
        if len(password.data) < 7:
            raise ValidationError('password must be up to 7 characters long')

        if not any(n.isupper() for n in password.data):
            raise ValidationError('password must contain capital letter')

        if not any(n.isdigit() for n in password.data):
            raise ValidationError('password must contain a number')
