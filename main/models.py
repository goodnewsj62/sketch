from datetime import datetime
import json

from flask_login import UserMixin

from . import db

follow = db.Table('follow',
                        db.Column('follower_id',db.Integer,db.ForeignKey('user.id')),
                        db.Column('followed_id',db.Integer, db.ForeignKey('user.id'))
                        )



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    social_id = db.Column(db.String(50),nullable=True,unique=True)
    username = db.Column(db.String(50), unique=True,nullable=False)
    password = db.Column(db.String,nullable=False)
    email = db.Column(db.String(50), nullable=True,unique=True)
    contact = db.Column(db.String(16), nullable=True,unique=True)
    avatar_id = db.Column(db.String(50), nullable=False,default="avatar.jpg")
    accounts= db.Column(db.String(200),nullable=True,unique=True)
    bio = db.Column(db.String(110),nullable=True)
    notified = db.relationship('User', secondary=follow,primaryjoin = (follow.c.follower_id == id),
                                        secondaryjoin=(follow.c.followed_id == id),
                                        backref= db.backref('follow',lazy='dynamic'), lazy='dynamic'
                            )
    notification = db.relationship('Notification', backref='user_not',lazy='dynamic')
    post = db.relationship('Post',backref='posts',lazy=True)

    def __repr__(self):
        return '<{},{} object>'.format(self.name, self.username)

    def add_notification(self,title,data):
        #check if notifications is larger than needed
        if len(self.user_not) > 200:
            id_ = self.user_not[0].id
            del_ = Notification.query.get(id_)
            db.session.delete(del_)
            db.session.commit()
            del self.user_not[0]

        n = Notification(title = title, user_id= self, pay_load= json.dumps(data))
        db.session.add(n)
        db.session.commit()



    # checks if user is following provided user
    def is_following(self,user):
        return self.notified.filter(follow.c.followed_id == user.id).count() > 0

class Post(db.Model):
    id = db.Column(db.Integer,primary_key= True)
    label = db.Column(db.String(30), nullable=False, unique=True)
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200),nullable=True)
    date_posted = db.Column(db.DateTime,nullable=False, default=datetime.utcnow)
    love = db.Column(db.Integer, nullable=False, default=0)
    private = db.Column(db.Boolean, nullable=False,default=False)
    uploader = db.Column(db.Integer,db.ForeignKey('user.id', ondelete='CASCADE'),nullable=False)
    category = db.relationship('Categories', backref = "categories", lazy = "dynamic")

    def __repr__(self):
        return '<{} object>'.format(self.title)


class Notification(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(200), nullable= False)
    time_stamp = db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    pay_load = db.Column(db.Text)

    def __repr__(self):
        return "<{} from {}>".format(self.title,self.user_id)

    def get_load(self):
        return json.loads(str(self.pay_load))

class Categories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    catlog = db.Column(db.Text, nullable=False)
    post = db.Column(db.Integer,db.ForeignKey('post.id', ondelete='CASCADE'),nullable=False)

    def __repr__(self):
        return "<{}>".format(self.catlog)

    def get_category(self):
        return json.loads(str(self.catlog))

