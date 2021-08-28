from datetime import datetime
from enum import unique
import json

from flask_login import UserMixin

from . import db

#the follower are the ones following thoes on the right hand side of the table (followed)
follow = db.Table('follow',
                        db.Column('follower_id',db.Integer,db.ForeignKey('user.id')),
                        db.Column('followed_id',db.Integer, db.ForeignKey('user.id'))
                        )



class User(UserMixin, db.Model):
    #when quering the following row you get the result of those you are
    #following (users on the right hand side of the table "follow.c.followed_id") vice versal
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    social_id = db.Column(db.String(50),nullable=True,unique=True)
    username = db.Column(db.String(50), unique=True,nullable=False)
    password = db.Column(db.String,nullable=False)
    email = db.Column(db.String(100), nullable=True,unique=True)
    contact = db.Column(db.String(16), nullable=True,unique=True)
    avatar_id = db.Column(db.String(50), nullable=False,default="avatar.jpg")
    accounts= db.Column(db.String(200),nullable=True,unique=True)
    bio = db.Column(db.String(110),nullable=True)
    following = db.relationship('User', secondary=follow,primaryjoin = (follow.c.follower_id == id),
                                        secondaryjoin=(follow.c.followed_id == id),
                                        backref= db.backref('followers',lazy='dynamic'), lazy='dynamic'
                            )
    notifications = db.relationship('Notification', backref='user',lazy='dynamic')
    posts = db.relationship('Post',backref='posts',lazy=True)


    def __repr__(self):
        return '<{},{} object>'.format(self.name, self.username)

    def follow(self, user):
        if not self.is_following(user):
            self.following.append(user.id)

    def unfollow(self,user):
        if self.is_following(user):
            self.following.remove(user.id)

    def is_following(self,user):
        return self.following.filter(follow.c.followed_id == user.id).count() > 0
    
    def add_notification(self,title,data):
        #check if notifications is larger than needed
        if self.notification.count() > 300:
            db.session.delete(self.notifications[0])
        notification_obj = Notification(title=title)
        notification_obj.payload(data)
        db.session.add()
        return notification_obj
        

class Post(db.Model):
    id = db.Column(db.Integer,primary_key= True)
    label = db.Column(db.String(30), nullable=False, unique=True)
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200),nullable=True)
    date_posted = db.Column(db.DateTime,nullable=False, default=datetime.utcnow)
    love = db.Column(db.Integer, nullable=False, default=0)
    private = db.Column(db.Boolean, nullable=False,default=False)
    uploader = db.Column(db.Integer,db.ForeignKey('user.id', ondelete='CASCADE'),nullable=False)
    category = db.Column(db.String(100), db.ForeignKey('category.name', ondelete='CASCADE'),nullable=False)

    def __repr__(self):
        return '<{} object>'.format(self.title)


class Notification(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(200), nullable= False)
    time_stamp = db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    payload = db.Column(db.Text)

    def __repr__(self):
        return "<{} from {}>".format(self.title,self.user_id)

    @property 
    def payload(self):
        return json.loads(str(self._payload))
    
    @payload.setter
    def payload(self,payload):
        if not isinstance(payload,dict):
            raise TypeError("Must be an instance of type dict")
        setattr(self,"payload", json.dumps(payload))

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True)
    posts = db.relationship('Post',backref='categories',lazy=True)

    def __repr__(self):
        return "<{}>".format(self.catlog)

