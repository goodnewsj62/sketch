from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import Email,DataRequired,Length,ValidationError
from flask_wtf.file import FileRequired,FileAllowed,FileField


from ..database import Database
from ..models import User,Role,Post,Notification,follow

db = Database(User,Post,Notification,follow)

class UpdateProfile(FlaskForm):
    name = StringField("name", validators=[DataRequired(),Length(min=3,max=50)])
    username = StringField("username", validators=[DataRequired(),Length(min=3,max=50)])
    email = StringField("email",validators=[DataRequired(),Length(min=5,max=50),Email()])
    contact = StringField('phone no',validators=[Length(min=5,max=15)])
    facebook = StringField('facebook username', validators=[Length(min=3,max=50)])
    instagram = StringField('instagram', validators=[Length(min=3,max=50)])
    twitter = StringField('twitter', validators=[Length(min=3,max=50)])
    linkedin = StringField('linkedin', validators=[Length(min=3,max=50)])
    bio = StringField("bio", validators=[Length(max=105)])


    def validate_username(self,username):
        if db.get_user_by_username(username):
            raise ValidationError('username already exist')
    
    def validate_email(self,email):
        if len(email) == 0:
            raise ValidationError('please enter an email')
        if db.get_user_by_email(email):
            raise ValidationError('email already exist')

class AvatarForm(FlaskForm):
    photo = FileField("photo", validators=[FileRequired(),FileAllowed(["jpg","png"],"Image files only!")])